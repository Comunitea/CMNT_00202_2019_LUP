# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
#from odoo.exceptions import RedirectWarning, UserError, ValidationError



class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    order_message_ids = fields.One2many(comodel_name="sale.order.message",
                                  inverse_name='purchase_id',
                                  string="Messages")
  