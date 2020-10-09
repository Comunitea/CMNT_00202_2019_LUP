# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):

    _inherit = "mrp.workorder"

    sheet_id = fields.Many2one(
        'cost.sheet', 'Cost Sheet', related='production_id.sheet_id')
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
    planned_qty = fields.Float(
        'Cantidad planificada')
    employee_id = fields.Many2one('hr.employee', 'Asignado a')
    group_mrp_id = fields.Many2one('group.production', 'Group', readonly=True)

    @api.depends('machine_time_ids.time')
    def _get_machine_time(self):
        for wo in self:
            wo.machine_time = sum([x.time for x in wo.machine_time_ids])

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
        in_pick.action_confirm()

        self.write({
            'in_pick_id': in_pick.id,
            'out_pick_id': out_pick.id
        })
        return


class MachineTime(models.Model):

    _name = "machine.time"

    workorder_id = fields.Many2one('mrp.workorder')
    time = fields.Float('Horas máquina')
