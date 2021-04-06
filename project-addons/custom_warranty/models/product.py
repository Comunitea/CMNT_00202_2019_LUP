# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def _get_default_warranty_duration(self):
        if self.tracking == 'none':
            return self.env['ir.config_parameter'].sudo().get_param('product.default_warranty', default=0)
        else:
            return 0

    life_time = fields.Integer(
        "Warranty duration (in days)", default=_get_default_warranty_duration
    )
    with_warranty = fields.Boolean('Serial Register', default=False)

    def action_open_product_lot(self):
        action = super().action_open_product_lot()
        if self.with_warranty:
            form_id = self.env.ref('stock.view_production_lot_form').read()[0]['id']
            tree_id = self.env.ref('custom_warranty.view_serial_warranty').read()[0]['id']
            action['views'] = [(tree_id, 'tree'), (form_id, 'form')]
        return action



class ProductProduct(models.Model):

    _inherit = "product.product"
    
    def action_open_product_lot(self):
        action = super().action_open_product_lot()
        if self.with_warranty:
            form_id = self.env.ref('stock.view_production_lot_form').read()[0]['id']
            tree_id = self.env.ref('custom_warranty.view_serial_warranty').read()[0]['id']
            
            action['views'] = [(tree_id, 'tree'), (form_id, 'form')]
            # action['name'] = 'Serial Warranties'
            # action['context'] = {'product_id': self.id, 'search_default_under_warranty': 1}
        return action