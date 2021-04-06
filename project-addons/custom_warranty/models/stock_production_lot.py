# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    with_warranty = fields.Boolean(related="product_id.with_warranty")
    sale_date = fields.Date('Sale date')
    life_date = fields.Date('End warranty')
    under_warranty = fields.Boolean('Under warranty')
    warranty_partner_id = fields.Many2one('res.partner', string='Warranty Partner')

    def check_warranties(self):
        
        domain = [('under_warranty', '=', True), ('life_date', '<', fields.Date.today())]
        self.search(domain).write({'under_warranty': False})
    

