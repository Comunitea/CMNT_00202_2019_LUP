# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    group_sheets_count = fields.Integer('Grupo de costes',
                                  compute='_count_sheets')
    sheets_count = fields.Integer('Hojas de coste',
                                  compute='_count_sheets')
    production_count = fields.Integer('Productions',
                                compute='_count_production_and_task')
    count_task = fields.Integer('Productions',
                                compute='_count_production_and_task')
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
    def _count_production_and_task(self):
        for order in self:
            order.production_count = len(
                order.get_sheet_lines().mapped('production_id'))
            order.count_task = len(
                order.get_sheet_lines().mapped('task_id'))
    
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
    def view_tasks(self):
        self.ensure_one()
        action = self.env.ref(
            'project.act_project_project_2_project_task_all').read()[0]
        if self.project_id and self.project_id.task_ids:
            tasks = self.project_id.task_ids
            # action['domain'] = [('id', 'in', tasks.ids)]
            action['context'] = {
                'search_default_project_id': [self.project_id.id],
                'default_project_id': self.project_id.id,
            }
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    @api.multi
    def view_productions(self):
        self.ensure_one()
        productions = self.get_sheet_lines().filtered(
            lambda s: s.sheet_type != 'design'
        ).mapped('production_id')
        if productions:
            action = self.env.ref(
                'mrp.mrp_production_action').read()[0]
        
            action['domain'] = [('id', 'in', productions.ids)]
            
        else:
            action = {'type': 'ir.actions.act_window_close'}
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
        for order in self:
            prods = order.get_sheet_lines().mapped('production_id')
            prods.action_cancel()
            prods.unlink()
        return res

class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    group_sheet_id = fields.Many2one(
        'group.cost.sheet', 'Hojas de coste', readonly=True)
    ref = fields.Char('Referencia')
    
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
    