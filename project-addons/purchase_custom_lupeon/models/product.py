# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import *


class ProductProduct(models.Model):
    _inherit = "product.product"

    twelve_months_ago = fields.Float()
    six_months_ago = fields.Float() 
    last_month_ago = fields.Float() 
    main_supplier_id = fields.Many2one('res.partner', 'Main Supplier',
                                       compute="_compute_supplier_info",
                                       search="_search_main_supplier",
                                       store=False)
    supplier_min_qty = fields.Float('Supplier min qty',
                                    compute="_compute_supplier_info")
    supplier_price = fields.Float('Supplier Price',
                                  compute="_compute_supplier_info")
    supplier_delay =fields.Integer('Supplier Delay',
                                   compute="_compute_supplier_info")
    purchase_qty = fields.Float('Purchase',
                                compute="_compute_supplier_info",
                                readonly=True)
    actual_po_id = fields.Many2one('purchase.order', 'Actual Purchase',
                                       compute="_compute_supplier_info",
                                    ) 
    stock_coverage = fields.Float('Cobertura',
                                compute="_compute_supplier_info",
                                readonly=True)
    
    @api.multi
    def _search_main_supplier(self, operator, value):
        return [("seller_ids.name", operator, value)]

    @api.depends('seller_ids', 'seller_ids.name', 'seller_ids.price')
    def _compute_supplier_info(self):
       
        for product in self:
            sellers = product.seller_ids
            if sellers:
                product.nbr_suppliers = len(sellers)
                product.supplier_min_qty = sellers[0].min_qty
                product.supplier_price = sellers[0].price
                product.supplier_delay = sellers[0].delay
                product.main_supplier_id = sellers[0].name
            else:
                product.nbr_suppliers = 0
                product.supplier_min_qty = 0
                product.supplier_price = 0
                product.supplier_delay = 0
                product.main_supplier_id = False
            pol = self.env['purchase.order.line'].search([
                ('product_id', '=', product.id),
                ('state','not in',['purchase','cancel','done'])])
            if pol:
                product.purchase_qty = sum(pol.mapped("product_qty"))
                product.actual_po_id = pol[0].order_id
            else:
                product.purchase_qty = 0
                product.actual_po_id = False
            div = (product.twelve_months_ago/365*0.2) + (product.six_months_ago/180*0.5) + (product.last_month_ago/30*0.3)
            if div != 0:
                stock_coverage = product.qty_available / div
                product.stock_coverage = stock_coverage
            else:
                product.stock_coverage = 0
                
           
    
    @api.model
    def compute_last_sales(self, products=False):
        twelve_months_ago = fields.Datetime.now() + relativedelta(months=-12)
        six_months_ago = fields.Datetime.now() + relativedelta(months=-6)
        last_month_ago = fields.Datetime.now() + relativedelta(months=-1)
        
        if not products:
            products = self.search([("type", "!=", "service")])
        for product in products:
            sale_lines_12 = self.env["sale.order.line"].search(
                [
                    ("product_id", "=", product.id),
                    ("order_id.date_order", ">=", twelve_months_ago),
                    ("state", "not in", ('draft', 'sent', 'cancel')),
                ]
            )
            sale_lines_6 = self.env["sale.order.line"].search(
                [
                    ("product_id", "=", product.id),
                    ("order_id.date_order", ">=", six_months_ago),
                    ("state", "not in", ('draft', 'sent', 'cancel')),
                ]
            )
            sale_lines_1 = self.env["sale.order.line"].search(
                [
                    ("product_id", "=", product.id),
                    ("order_id.date_order", ">=", last_month_ago),
                    ("state", "not in", ('draft', 'sent', 'cancel')),
                ]
            )
            product.twelve_months_ago = sum(
                sale_lines_12.mapped("product_uom_qty")
            )
            product.six_months_ago = sum(
                sale_lines_6.mapped("product_uom_qty")
            )
            product.last_month_ago = sum(
                sale_lines_1.mapped("product_uom_qty")
            )

    def button_compute_last_sales(self):
        self.compute_last_sales(self)

    def get_unreceived_items(self):
        model_data = self.env["ir.model.data"]

        tree_view = model_data.get_object_reference(
            "purchase_custom_lupeon", "purchase_custom_tree"
        )
        search_view = model_data.get_object_reference(
            "purchase_custom_lupeon", "purchase_custom_search"
        )
        domain = [("product_id", "=", self.id)]
        value = {}
        for call in self:
            value = {
                "name": _("Purchase order lines"),
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "purchase.order.line",
                "views": [(tree_view and tree_view[1] or False, "tree")],
                "type": "ir.actions.act_window",
                "domain": domain,
                "search_view_id": search_view and search_view[1] or False,
                "context": {'search_default_in_1_stock': 1},
            }
        return value

    def create_order_point(self):
        for prod in self:
            op_ex = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', prod.id), ('company_id', '=', 2)])
            if not op_ex:
                vals = {
                'product_id': prod.id,
                #'computed': True,
                'product_min_qty':0,
                'product_max_qty':0,
                'company_id': 2
                }
                if prod.variant_seller_ids:
                    days = max(prod.variant_seller_ids.mapped('delay'))
                    if days:
                        vals['lead_days'] = days
                op = self.env['stock.warehouse.orderpoint'].create(vals)
                #op.compute_orderpoint_quantities()

