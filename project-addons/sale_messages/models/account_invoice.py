# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
#from odoo.exceptions import RedirectWarning, UserError, ValidationError



class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    sale_message_ids = fields.One2many(comodel_name="sale.order.message",
                                inverse_name="invoice_id",
                               compute="_compute_messages_ids")
    sale_message_count = fields.Integer("number of messages", compute="_compute_messages_ids")


    @api.multi
    def _compute_messages_ids(self):
        for inv in self:
            sale_ids = inv.mapped('invoice_line_ids').mapped('sale_line_ids').mapped('order_id')
            inv_messages = sale_ids.mapped('order_message_ids').filtered(lambda r: r.invoice_available)
            inv.sale_message_ids = inv_messages.ids
            inv.sale_message_count = len(inv_messages)
    
