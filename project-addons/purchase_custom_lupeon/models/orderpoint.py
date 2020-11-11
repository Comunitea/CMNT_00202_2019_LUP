# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import timedelta
from dateutil.relativedelta import *


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"
    
    computed = fields.Boolean("Computed", default=False)
    
    @api.model
    def compute_orderpoint_quantities(self, orderpoints=False):
        
        
        if not orderpoints:
            orderpoints = self.search([('computed', '=', True)])
        for orderpoint in orderpoints:
            if not orderpoint.computed:
                raise UserError(
                _('Esta abastecimiento no está configurado para ser calculado')) 
            value = 0.0
            value = (orderpoint.product_id.twelve_months_ago/365)*0.2 + (orderpoint.product_id.six_months_ago/180)*0.5 + (orderpoint.product_id.last_month_ago/30) * 0.3
            min_qty = value * orderpoint.lead_days
            max_qty = min([min_qty * 2, value * 30 ])
            orderpoint.write(
                {
                    "product_min_qty": min_qty,
                    "product_max_qty": max_qty,
                }
            )
                        

    def button_compute_orderpoint_quantities(self):
        self.compute_orderpoint_quantities(self)


