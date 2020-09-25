# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SaleOrder(models.Model):

    _inherit = "sale.order"

    group_sheets_count = fields.Integer('Grupo de costes',
                                  compute='_count_sheets')
    sheets_count = fields.Integer(string='Hojas de coste',
                                  compute='_count_sheets')
    purchase_count = fields.Integer(string='Compras',
                                    compute='_count_purchases')
    production_count = fields.Integer('Productions',
                                compute='_count_production_and_task')
    count_task = fields.Integer('Productions',
                                compute='_count_production_and_task')
    project_id = fields.Many2one('project.project', 'Project', readonly=True,
        copy=False)
    production_date = fields.Datetime('Fecha producción')
    # Sobrescribo del todo para tener el orden correcto en el estado de design
    # el statusbar_visible no lo ordena
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('design', 'Design'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, 
        index=True, track_visibility='onchange', track_sequence=3,
        default='draft')

    purchase_ids = fields.One2many(
        'purchase.order', 'dest_sale_id', 'Purchases')

    @api.multi
    def action_design(self):
        for order in self:
            # Creo las tareas y producciones asociadas a cada hoja de costes
            sheet_lines = order.get_sheet_lines()
            sheet_lines.create_tasks()
        return self.write({'state': 'design'})

    @api.onchange('commitment_date')
    def _onchange_commitment_date(self):
        res = super()._onchange_commitment_date()
        if self.commitment_date:
            self.production_date = self.commitment_date - timedelta(days=3)
        return res

    @api.onchange('production_date')
    def _onchange_production_date(self):
        """ Warn if the production date is later than the commitment date """
        if (self.commitment_date and self.production_date and self.commitment_date < self.production_date):
            self.production_date = self.commitment_date - timedelta(days=3)
            return {
                'warning': {
                    'title': _('Production date is too late.'),
                    'message': _("The production date is later than the \
                                 commitment date.")
                }
            }

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
    def _count_purchases(self):
        for order in self:
            order.purchase_count = len(order.purchase_ids)

    @api.multi
    def _count_production_and_task(self):
        for order in self:
            boms = order.get_group_sheets().mapped('bom_id')
            domain = [('bom_id', 'in', boms.ids)]
            productions = order.get_sheet_lines().mapped('production_id')
            productions |= self.env['mrp.production'].search(domain)
            order.production_count = len(productions)
            order.count_task = \
                len(
                    order.get_sheet_lines().
                    mapped('time_line_ids.task_id')) + \
                len(
                    order.get_sheet_lines().
                    mapped('oppi_line_ids.task_id')) + \
                len(
                    order.get_sheet_lines().mapped('meet_line_ids.task_id'))

    @api.multi
    def view_purchases(self):
        self.ensure_one()
        action = self.env.ref(
            'purchase.purchase_form_action').read()[0]
        if len(self.purchase_ids) > 1:
            action['domain'] = [('id', 'in', self.purchase_ids.ids)]
        elif len(self.purchase_ids) == 1:
            form_view_name = 'purchase.purchase_order_form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = self.purchase_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def view_product_cost_sheets(self):
        self.ensure_one()
        sheets = self.get_group_sheets()
        action = self.env.ref(
            'cost_sheet_lupeon.action_product_cost_sheets').read()[0]
        if len(sheets) > 1:
            action['domain'] = [('id', 'in', sheets.ids)]
        elif len(sheets) == 1:
            form_view_name = 'cost_sheet_lupeon.product_cost_sheet_view_form'
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
            form_view_name = 'cost_sheet_lupeon.cost_sheet_view_form'
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

        boms = self.get_group_sheets().mapped('bom_id')
        domain = [('bom_id', 'in', boms.ids)]
        productions |= self.env['mrp.production'].search(domain)
        if productions:
            action = self.env.ref(
                'mrp.mrp_production_action').read()[0]

            action['domain'] = [('id', 'in', productions.ids)]

        else:
            action = {'type': 'ir.actions.act_window_close'}

        action['context'] = "{}"
        return action

    def create_sale_purchase(self):
        self.ensure_one()
        supplier_purchase = {}
        sheet_lines = self.get_sheet_lines()
        suppliers = sheet_lines.mapped('purchase_line_ids.partner_id')
        for partner in suppliers:
            vals = {
                'partner_id': partner.id,
                'origin': self.name,
                'dest_sale_id': self.id,
                'payment_term_id':
                partner.property_supplier_payment_term_id.id,
                'date_order': fields.Datetime.now()
            }
            po = self.env['purchase.order'].create(vals)
            supplier_purchase[partner.id] = po

        for line in sheet_lines.mapped('purchase_line_ids'):
            po = supplier_purchase[line.partner_id.id]
            taxes = line.product_id.supplier_taxes_id
            # fpos = po.fiscal_position_id
            # taxes_id = fpos.map_tax(
            #     taxes, line.product_id.id, line.partne_id.name) if fpos \
            #     else taxes

            vals = {
                'name': line.name or line.product_id.name,
                'product_qty': line.qty,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'price_unit': line.pvp_ud,
                'date_planned': fields.Datetime.now(),
                # 'taxes_id': [(6, 0, taxes_id.ids)],
                'taxes_id': [(6, 0, taxes.ids)],
                'order_id': po.id,
            }
            self.env['purchase.order.line'].create(vals)

    @api.multi
    def action_confirm(self):
        """
        Check if order requires client_order_ref.
        Creation of product sheet ids
        """
        for order in self:
            # Creo las tareas y producciones asociadas a cada hoja de costes
            sheet_lines = order.get_sheet_lines()
            sheet_lines.create_sale_productions()

            # Creo la lista de materiales asociada al grupo de costes
            group_costs = order.get_group_sheets()
            group_costs.create_bom_on_fly()

            # Creo las compras en borrador, agrupadas por proveedor
            order.create_sale_purchase()

        res = super().action_confirm()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self.mapped('project_id.task_ids').unlink()
        self.mapped('project_id').unlink()
        self.mapped('purchase_ids').unlink()
        for order in self:
            prods = order.get_sheet_lines().mapped('production_id')
            prods.action_cancel()
            prods.unlink()

            # boms = self.get_group_sheets().mapped('bom_id')
            # boms.unlink()


        return res

    def duplicate_with_costs(self):
        new = self.with_context(from_copy=True).copy()
        view = self.env.ref(
            'sale.view_order_form'
        )
        for line in new.order_line:
            line.group_sheet_id.write({'sale_line_id': line.id})
        return {
            'name': _('Duplicated'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': new._name,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'res_id': new.id,
            'context': self._context,
        }


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    group_sheet_id = fields.Many2one(
        'group.cost.sheet', 'Grupo de hojas coste', readonly=True)
    ref = fields.Char('Referencia')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not self._context.get('from_copy'):
            res.create_product_cost_sheet()
        return res

    def unlink(self):
        self.mapped('group_sheet_id').unlink()
        res = super().unlink()
        return res

    def create_product_cost_sheet(self):
        for line in self.filtered(lambda x: x.product_id.custom_mrp_ok):
            vals = {
                'sale_line_id': line.id,
                # 'name': line.order_id.name + ' - ' + line.name,
                'admin_fact': line.order_id.partner_id.admin_fact
            }
            line.group_sheet_id = self.env['group.cost.sheet'].create(vals)
        return

    def copy_data(self, default=None):
        if default is None:
            default = {}
        self.ensure_one()
        if self.group_sheet_id:
            copy_vals = {
                'bom_id': False,
                'sale_line_id': False,
            }
            new_sheet = self.group_sheet_id.copy(default=copy_vals)
            default['group_sheet_id'] = new_sheet.id

        res = super().copy_data(default)
        return res

    @api.multi
    def _get_display_price(self, product):
        res = super()._get_display_price(product)
        if product.custom_mrp_ok and self.group_sheet_id and \
                self.product_uom_qty:
            res = self.group_sheet_id.line_pvp / self.product_uom_qty
        return res
