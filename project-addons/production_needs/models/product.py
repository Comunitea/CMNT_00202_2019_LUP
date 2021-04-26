# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import *


class ProductProduct(models.Model):
    _inherit = "product.product"

    
    actual_production_id = fields.Many2one('mrp.production', 'Last Production',
                                       compute="_compute_production_info",
                                    ) 
    total_production_qty = fields.Float('Total en producciones',
                                compute="_compute_production_info",
                                readonly=True)
    
    def _compute_production_info(self):
       
        for product in self:
           
            prod = self.env['mrp.production'].search([
                ('product_id', '=', product.id),
                ('state','not in',['cancel','done'])])
            if prod:
                product.total_production_qty = sum(prod.mapped("product_qty"))
                product.actual_production_id = prod[0].id
            else:
                product.production_qty = 0
                product.actual_production_id = False
                
           
