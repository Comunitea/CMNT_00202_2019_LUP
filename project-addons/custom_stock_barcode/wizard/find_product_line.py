# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class FindProductLine(models.TransientModel):
    _name = "find.product.line"
    _description = "Wizard to scan SN/LN for specific product"

    scanned_product = fields.Char('Scanned code')
    product_id = fields.Many2one('product.product')
    
    @api.onchange('scanned_product')
    def _onchange_scanned_product(self):
        if self.scanned_product:
            scanned_product = "{}".format(self.scanned_product)
            product = self.env['product.product'].search([
                '|',
                ('barcode', '=', scanned_product),
                ('default_code', '=', scanned_product), ('type', '!=', 'service')
            ], limit=1)

            if product:
                self.product_id = product.id
            else:
                supplier_product = self.env['product.supplierinfo'].search([
                    ('product_code', '=', scanned_product), ('product_id', '!=', None)
                ], limit=1)

                if supplier_product:
                    self.product_id = supplier_product.product_id.id
                else:
                    self.scanned_product = None
        else:
            self.product_id = None
    
    def find_line(self):
        return self.product_id.id