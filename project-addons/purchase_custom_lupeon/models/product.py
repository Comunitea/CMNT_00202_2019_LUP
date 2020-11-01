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
    main_supplier_id = fields.Many2one('Mai Supplier ', compute="_compute_supplier_info")
    supplier_min_qty = fields.Float('Supplier min qty', compute="_compute_supplier_info")
    supplier_price = fields.Float('Supplier Price', compute="_compute_supplier_info")
    supplier_delay =fields.Integer('Supplier Delay', compute="_compute_supplier_info")
    
    
    def _compute_supplier_info(self):
        read_group_res = self.env['product.supplierinfo'].read_group(
            [('product_id', 'in', self.ids)],
            ['product_id', 'name', 'min_qty', 'price','delay'],
            ['product_id'])
        res = {i: {} for i in self.ids}
        for data in read_group_res:
            res[data['product_id'][0]]['name'] = data['name']
            res[data['product_id'][0]]['nbr_suppliers'] = int(data['product_id_count'])
            res[data['product_id'][0]]['min_qty'] = data['min_qty']
            res[data['product_id'][0]]['price'] = data['price']
            res[data['product_id'][0]]['delay'] = data['delay']
        for product in self:
            product.nbr_suppliers = res[product.id].get('nbr_suppliers', 0)
            product.supplier_min_qty = res[product.id].get('min_qty', 0)
            product.supplier_price = res[product.id].get('price', 0)
            product.supplier_delay = res[product.id].get('delay', 0)
            product.main_supplier_id =res[product.id].get('name', False)
    
    
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
            product.twelve_months_ago = sum(
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
