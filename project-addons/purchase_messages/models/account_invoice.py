# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
#from odoo.exceptions import RedirectWarning, UserError, ValidationError



class AccountInvoice(models.Model):

    _inherit = "account.invoice"


    @api.multi
    def _compute_messages_ids(self):
        for inv in self:
            sale_ids = inv.mapped('invoice_line_ids').mapped('sale_line_ids').mapped('order_id')
            inv_messages = sale_ids.mapped('order_message_ids').filtered(lambda r: r.invoice_available)

            purchase_ids = inv.mapped('invoice_line_ids').mapped('purchase_id')
            p_inv_messages = purchase_ids.mapped('order_message_ids').filtered(lambda r: r.invoice_available)

            inv.sale_message_ids = inv_messages.ids + p_inv_messages.ids
            inv.sale_message_count = len(inv.sale_message_ids)
    
