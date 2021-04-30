# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class GroupProduction(models.Model):

    _name = "group.production"
    _description = "Group Production"

    name = fields.Char('Name')
    note = fields.Text('Notas')

    workorder_ids = fields.One2many(
        'mrp.workorder', 'group_mrp_id', 'Gropued Productions',
        readonly=False)
    register_ids = fields.One2many(
        'group.register.line', 'group_mrp_id', 'Registro Producciones')

    material_ids = fields.One2many(
        'group.material.line', 'group_mrp_id', 'Materials to consume',
        readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Planificado'),
        ('progress', 'En progreso'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Estado',
        copy=False, default='draft', track_visibility='onchange')

    total_user_time = fields.Float('Tiempo usuario total', readonly=True)
    total_time = fields.Float('Tiempo máquina total', readonly=True)

    total_done = fields.Float('Total realizado', compute="_get_total_done")

    final_lot = fields.Char('Lote final')

    def _get_total_done(self):
        for gr in self:
            total = 0
            for reg in gr.register_ids:
                total += reg.qty_done
            gr.total_done = total


    def action_confirm_group(self):
        """
        Creo las líneas on los consumos agrtupados y enlazo las órdenes de
        trabajo al grupo
        """
        self.ensure_one()
        product_qtys = {}
        for reg in self.register_ids:
            # wo = prod.workorder_ids.filtered(lambda x: x.active_move_line_ids)

            wo = reg.workorder_id
            if not wo:
                raise UserError('La producción %s no tiene orden de trabajo')

            # Agrupo consumos
            for move in wo.active_move_line_ids:
                if move.product_id not in product_qtys:
                    product_qtys[move.product_id] = 0.0
                product_qtys[move.product_id] += move.qty_done

            # wo.group_mrp_id = self.id

        for product in product_qtys:
            vals = {
                'group_mrp_id': self.id,
                'product_id': product.id,
                'qty': product_qtys[product]
            }
            self.env['group.material.line'].create(vals)
        self.state = 'confirmed'

    def action_plan_group(self):
        self.ensure_one()
        # for wo in self.workorder_ids:
        #     if not wo.planned_qty:
        #         raise UserError(
        #             _('Debes planificar las cantidades a realizar'))
        for reg in self.register_ids:
            if not reg.qty_done:
                raise UserError(
                    _('Debes planificar las cantidades a realizar'))
        self.state = 'planned'

    def action_cancel_group(self):
        self.ensure_one()
        self.material_ids.unlink()
        self.workorder_ids.write({'group_mrp_id': False})
        self.state = 'cancel'

    def action_draft_group(self):
        self.ensure_one()
        self.state = 'draft'

    def unlink(self):
        for gr in self:
            gr.workorder_ids.write({'group_mrp_id': False})
        return super().unlink()


class GroupRegisterLine(models.Model):
    _name = 'group.register.line'
    _description = "Group Register Line"

    group_mrp_id = fields.Many2one(
        'group.production', 'Group', readonly=True, ondelete='cascade')
    workorder_id = fields.Many2one(
        'mrp.workorder', 'Orden de trabajo', readonly=True)
    th_machine_hours = fields.Float(
       'Horas máquina estimadas',
       related='workorder_id.th_machine_hours')
    th_user_hours = fields.Float(
       'Horas técnico estimadas',
       related='workorder_id.th_user_hours')
    production_id = fields.Many2one(
        'mrp.production', 'Producción Asociada',
        related='workorder_id.production_id')
    product_id = fields.Many2one(
        'product.product', 'Producto',
        related='workorder_id.product_id')
    product_qty = fields.Float(
        'Cantidad inicial',
        related='workorder_id.production_id.product_qty')
    qty_produced = fields.Float(
        'Cantidad producida',
        related='workorder_id.qty_produced')
    qty_pending = fields.Float('Pendiente', compute='_compute_pending')
    qty_done = fields.Float('Cantidad realizada')

    @api.depends('product_qty', 'qty_produced')
    def _compute_pending(self):
        for line in self:
            line.qty_pending = line.product_qty - line.qty_produced

    def unlink(self):
        self.mapped('workorder_id').write({'group_mrp_id': False})
        res = super().unlink()
        return res


class GroupMaterialLine(models.Model):

    _name = "group.material.line"
    _description = "Group Material Line"

    group_mrp_id = fields.Many2one('group.production', 'Group', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty = fields.Float('To consume', readonly=True)
    real_qty = fields.Float('Consumed quantity')
    pending = fields.Float('Pendiente', compute='_compute_pending')

    @api.depends('real_qty', 'qty')
    def _compute_pending(self):
        for line in self:
            line.pending = line.qty - line.real_qty
