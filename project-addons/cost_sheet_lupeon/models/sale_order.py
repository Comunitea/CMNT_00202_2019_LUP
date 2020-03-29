# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    group_sheets_count = fields.Integer('Product Costs',
                                  compute='_count_sheets')
    sheets_count = fields.Integer('Sheet Costs',
                                  compute='_count_sheets')
    project_id = fields.Many2one('project.project', 'Project', readonly=True)
    
    def get_group_sheets(self):
        self.ensure_one()
        return self.mapped('order_line.group_sheet_id')

    def get_sheet_lines(self):
        return self.mapped('order_line.group_sheet_id.sheet_ids')

    @api.multi
    def _count_sheets(self):
        for order in self:
            order.group_sheets_count = len(order.get_group_sheets())
            order.sheets_count = len(order.get_sheet_lines())
    
    @api.multi
    def view_product_cost_sheets(self):
        self.ensure_one()
        sheets = self.get_group_sheets()
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
    def view_sheets_lines(self):
        self.ensure_one()
        sheets = self.get_sheet_lines()
        action = self.env.ref(
            'cost_sheet_lupeon.action_cost_sheets').read()[0]
        if len(sheets) > 1:
            action['domain'] = [('id', 'in', sheets.ids)]
        elif len(sheets) == 1:
            form_view_name = 'cost_sheet_view_form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = sheets.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        action['context'] = {
            'search_default_group_line': self.id,
        }
        return action

    @api.multi
    def action_confirm(self):
        """
        Check if order requires client_order_ref.
        Creation of product sheet ids
        """
        for order in self:
            if (order.partner_id.require_num_order):
                order.client_order_ref = 'PENDIENTE'

            sheet_lines = order.get_sheet_lines()
            sheet_lines.create_task_or_production()
        
        res = super().action_confirm()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self.mapped('project_id.task_ids').unlink()
        self.mapped('project_id').unlink()
        return res

class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    group_sheet_id = fields.Many2one(
        'group.cost.sheet', 'Cost Sheets', readonly=True)
    
    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.create_product_cost_sheet()
        return res

    def unlink(self):
        self.mapped('group_sheet_id').unlink()
        res = super().unlink()
        return res

    def create_product_cost_sheet(self):
        for line in self:
            vals = {
                'sale_line_id': line.id,
                # 'name': line.order_id.name + ' - ' + line.name,
                'admin_fact': line.order_id.partner_id.admin_fact
            }
            line.group_sheet_id = self.env['group.cost.sheet'].create(vals)
        return
    