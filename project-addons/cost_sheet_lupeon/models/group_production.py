# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class GroupProduction(models.Model):

    _name = "group.production"

    name = fields.Char('Name')
    production_ids = fields.One2many(
        'mrp.production', 'group_mrp_id', 'Gropued Productions',
        readonly=True)

    workorder_ids = fields.One2many(
        'mrp.workorder', 'group_mrp_id', 'Gropued Productions',
        readonly=True)

    material_ids = fields.One2many(
        'group.material.line', 'group_mrp_id', 'Materials to consume',
        readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'En progreso'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='Estado',
        copy=False, default='draft', track_visibility='onchange')

    total_time = fields.Float('Total time', readonly=True)

    def action_confirm_group(self):
        self.ensure_one()
        product_qtys = {}
        for prod in self.production_ids:
            wo = prod.workorder_ids.filtered(lambda x: x.active_move_line_ids)
            if not wo or wo.state not in ('ready', 'progress'):
                raise UserError('La producción %s no tiene orden de trabajo \
                    o no está en un estado de preparada o en proceso')

            # Agrupo consumos
            for move in wo.active_move_line_ids:
                if move.product_id not in product_qtys:
                    product_qtys[move.product_id] = 0.0
                product_qtys[move.product_id] += move.qty_done

            wo.group_mrp_id = self.id

        for product in product_qtys:
            vals = {
                'group_mrp_id': self.id,
                'product_id': product.id,
                'qty': product_qtys[product]
            }
            self.env['group.material.line'].create(vals)
        self.state = 'confirmed'

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
            gr.production_ids.write({'group_mrp_id': False})
            gr.workorder_ids.write({'group_mrp_id': False})
        return super().unlink()


class GroupMaterialLine(models.Model):

    _name = "group.material.line"

    group_mrp_id = fields.Many2one('group.production', 'Group', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty = fields.Float('To consume', readonly=True)
    real_qty = fields.Float('Consumed quantity')
    pending = fields.Float('Pendiente', compute='_compute_pending')

    @api.depends('real_qty', 'qty')
    def _compute_pending(self):
        for line in self:
            line.pending = line.qty - line.real_qty
