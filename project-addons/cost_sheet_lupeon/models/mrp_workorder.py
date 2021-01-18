# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpWorkorder(models.Model):

    _inherit = "mrp.workorder"

    sheet_id = fields.Many2one(
        'cost.sheet', 'Cost Sheet', related='production_id.sheet_id')
    th_machine_hours = fields.Float(
       'Horas máquina estimadas',
       compute="_get_th_machine_hours")
    e_partner_id = fields.Many2one(
        'res.partner', 'Proveedor Externalización', readonly=True)
    out_pick_id = fields.Many2one('stock.picking', 'Albarán salida',
                                  readonly=True)
    in_pick_id = fields.Many2one('stock.picking', 'Albarán entrada',
                                 readonly=True)
    machine_time_ids = fields.One2many('machine.time', 'workorder_id',
                                       'Machine times')
    machine_time = fields.Float(
        'Horas máquina total', compute="_get_machine_time")
    th_user_hours = fields.Float(
        'Horas técnico estimadas', compute="_get_th_user_time")
    employee_id = fields.Many2one('hr.employee', 'Asignado a')
    group_mrp_id = fields.Many2one('group.production', 'Group', readonly=True)

    duration_expected_hours = fields.Float(
        'Duración horas',
        compute="_get_duration_hours")

    @api.depends('duration_expected')
    def _get_duration_hours(self):
        for wo in self:
            wo.duration_expected_hours = wo.duration_expected / 60

    @api.depends('machine_time_ids.time')
    def _get_machine_time(self):
        for wo in self:
            wo.machine_time = sum([x.time for x in wo.machine_time_ids])

    def _get_th_machine_hours(self):
        for wo in self:
            machine_time = wo.sheet_id.machine_hours
            # Para las producciones repetidas calculamos el factor
            factor = machine_time / wo.sheet_id.cus_units
            wo.th_machine_hours = wo.qty_production * factor

    def _get_th_user_time(self):
        for wo in self:
            tech_line = wo.sheet_id.workforce_cost_ids.filtered(
                lambda x: x.name == 'Horas Técnico'
            )
            duration = tech_line.hours if tech_line else 0
            oppi = wo.sheet_id.oppi_line_ids.filtered(
                lambda o: wo.name == o.name)
            if oppi:
                duration = oppi.time
            factor = duration / wo.sheet_id.cus_units
            wo.th_user_hours = wo.qty_production * factor

    # No quiero que cree checks de calidad
    def _create_checks(self):
        return

    # No quiero que cree checks de calidad
    def record_production(self):
        self.ensure_one()
        if self.e_partner_id:
            if not self.out_pick_id or self.out_pick_id.state != 'done':
                raise UserError(
            _('El albarán de salida de externalización debe estar realizado'))
            if not self.in_pick_id or self.in_pick_id.state != 'done':
                raise UserError(
            _('El albarán de entrada de externalización debe estar realizado'))

        return super().record_production()

    def get_pick_vals(self, p_type, orig_loc, dest_loc):
        self.ensure_one()
        vals = {
            'origin': self.display_name,
            'partner_id': self.e_partner_id.id,
            # 'date_done': order.date_order,
            'picking_type_id': p_type.id,
            # 'company_id': order.company_id.id,
            'move_type': 'direct',
            'location_id': orig_loc.id,
            'location_dest_id': dest_loc.id,
        }
        return vals

    def get_move_vals(self, pick, orig_loc, dest_loc, dest_move=False):
        self.ensure_one()
        move = self.production_id.move_finished_ids[0]
        vals = {
            'picking_id': pick.id,
            'name': move.product_id.name,
            'product_uom': move.product_id.uom_id.id,
            # 'picking_type_id': p_type.id,
            'product_id': move.product_id.id,
            'product_uom_qty': move.product_uom_qty,
            # 'state': 'draft',
            'location_id': orig_loc.id,
            'location_dest_id': dest_loc.id,
            'move_dest_id': dest_move,
        }
        return vals

    def create_pickings(self):
        # stock_loc = self.env.ref('stock.stock_location_stock')
        prod_loc = self.env.ref('stock.location_production')
        e_loc = self.env.ref('cost_sheet_lupeon.location_externalization')
        p_type_out = self.env.ref('cost_sheet_lupeon.externalization_out')
        p_type_in = self.env.ref('cost_sheet_lupeon.externalization_in')

        out_pick_vals = self.get_pick_vals(p_type_out, prod_loc, e_loc)
        out_pick = self.env['stock.picking'].create(out_pick_vals)

        in_pick_vals = self.get_pick_vals(p_type_in, e_loc, prod_loc)
        in_pick = self.env['stock.picking'].create(in_pick_vals)

        move_in_vals = self.get_move_vals(in_pick, e_loc, prod_loc)
        move_in = self.env['stock.move'].create(move_in_vals)

        move_out_vals = self.get_move_vals(
            out_pick, prod_loc, e_loc, move_in.id)
        self.env['stock.move'].create(move_out_vals)
        out_pick.action_confirm()

        out_pick.state = 'quality'
        # in_pick.action_confirm()

        self.write({
            'in_pick_id': in_pick.id,
            'out_pick_id': out_pick.id
        })
        return

    def _generate_lot_ids(self):
        """
        OVERWRITE
        Corrijo para que cre un move line por cada move_line del movbimiento, y con el
        lote que se reservó ya puesto 
        """
        self.ensure_one()
        MoveLine = self.env['stock.move.line']
        tracked_moves = self.move_raw_ids.filtered(
            lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id != self.production_id.product_id and move.bom_line_id)
        for move in tracked_moves:
            qty = move.unit_factor * self.qty_producing
            if move.product_id.tracking == 'serial':
                while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                    MoveLine.create({
                        'move_id': move.id,
                        'product_uom_qty': 0,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': min(1, qty),
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                    })
                    qty -= 1
            else:
                for ml in move.move_line_ids:
                    MoveLine.create({
                        'move_id': move.id,
                        'product_uom_qty': 0,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': ml.product_uom_qty,
                        'product_id': move.product_id.id,
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'done_wo': False,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id': ml.lot_id.id
                        })


class MachineTime(models.Model):

    _name = "machine.time"

    workorder_id = fields.Many2one('mrp.workorder')
    time = fields.Float('Horas máquina')


class MrpWorkcenterProductivity(models.Model):

    _inherit = "mrp.workcenter.productivity"

    duration_hours = fields.Float(
        'Duración horas',
        compute="_get_duration_hours")

    @api.depends('duration')
    def _get_duration_hours(self):
        for line in self:
            line.duration_hours = line.duration / 60
