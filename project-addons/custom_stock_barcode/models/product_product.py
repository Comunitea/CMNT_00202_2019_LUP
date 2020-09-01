# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_all_products_by_default_code(self):
        products = self.env['product.product'].search_read(
            [('default_code', '!=', None), ('type', '!=', 'service')],
            ['default_code', 'display_name', 'uom_id', 'tracking']
        )
        return {product.pop('default_code'): product for product in products}

    @api.model
    def get_all_products_by_provider_code(self):
        products = self.env['product.product'].search_read(
            [('default_code', '!=', None), ('type', '!=', 'service')],
            ['default_code', 'display_name', 'uom_id', 'tracking']
        )
        suppliers = self.env['product.supplierinfo'].search_read(
            [('product_code', '!=', None), ('product_id', '!=', None)],
            ['product_code', 'product_id']
        )
        # for each supplier, grab the corresponding product data
        to_add = []
        to_read = []
        products_by_id = {product['id']: product for product in products}
        for supplier in suppliers:
            supplier['product_id']
            if products_by_id.get(supplier['product_id']):
                product = products_by_id[supplier['product_id']]
                to_add.append(dict(product, **{'qty': supplier['qty']}))
            
            to_read.append((supplier, supplier['product_id'][0]))
        products_to_read = self.env['product.product'].browse(list(set(t[1] for t in to_read))).sudo().read(['display_name', 'uom_id', 'tracking'])
        products_to_read = {product['id']: product for product in products_to_read}
        to_add.extend([dict(t[0], **products_to_read[t[1]]) for t in to_read])
        return {product.pop('default_code') if 'default_code' in product else product.pop('product_code'): product for product in to_add}