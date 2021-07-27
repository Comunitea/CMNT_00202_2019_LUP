# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
#from odoo.exceptions import RedirectWarning, UserError, ValidationError


  
class SaleOrderMessage(models.Model):
    _inherit = "sale.order.message"



    purchase_id = fields.Many2one(comodel_name='purchase.order', string="Purchase Order")
    

