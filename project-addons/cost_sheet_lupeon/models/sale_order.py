# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sheets_count = fields.Integer('Product Costs',
                                  compute='_count_sheets')

    @api.multi
    def _count_sheets(self):
        for order in self:
            order.sheets_count = len(order.order_line.mapped('group_sheet_id'))
    
    @api.multi
    def view_product_cost_sheets(self):
        self.ensure_one()
        sheets = self.order_line.mapped('group_sheet_id')
        action = self.env.ref(
            'cost_sheet_lupeon.action_product_cost_sheets').read()[0]
        if len(sheets) > 1:
            action['domain'] = [('id', 'in', sheets.ids)]
        elif len(sheets) == 1:
            form_view_name = 'product_cost_sheet_view_form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = sheets.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        # action['context'] = {
        #     'search_default_group_line': self.id,
        # }
        return action

    @api.multi
    def action_confirm(self):
        """
        Check if order requires client_order_ref.
        Creation of product sheet ids
        """
        for order in self:
            if (
                order.partner_id.require_num_order
            ):
                order.client_order_ref = 'PENDIENTE'

            import ipdb; ipdb.set_trace()
            cost_sheets = order.order_line.mapped('group_sheet_id')
        
        res = super().action_confirm()
        return res



class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    group_sheet_id = fields.Many2one(
        'product.cost.sheet', 'Cost Sheets')
    
    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.create_product_cost_sheet()
        return res
    
    def unlink(self, vals):
        res = super().unlink(vals)
        line.mapped('group_sheet_id').unlink()
        return res

    def create_product_cost_sheet(self):
        for line in self:
            vals = {
                'sale_line_id': line.id,
                # 'name': line.order_id.name + ' - ' + line.name,
                'admin_fact': line.order_id.partner_id.admin_fact
            }
            line.group_sheet_id = self.env['product.cost.sheet'].create(vals)
        return
    