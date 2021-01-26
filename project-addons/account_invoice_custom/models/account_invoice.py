# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        invoices_no_date = self.filtered(lambda inv: not inv.date and
                                        inv.type in ('in_invoice', 'in_refund'))
        if invoices_no_date:
            invoices_no_date.write({'date': fields.Date.today()})
        return super(AccountInvoice, self).action_move_create()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            if self.partner_id.user_id:
                self.user_id = self.partner_id.user_id.id or self.env.uid
            if self.type == 'out_refund':
                self.payment_mode_id = self.with_context(
                    force_company=self.company_id.id,
                ).partner_id.customer_payment_mode_id
        return res

    @api.multi
    def _check_duplicate_supplier_reference(self):
        for invoice in self:
            # refuse to validate a vendor bill/credit note if there already exists one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/credit note
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search([('type', '=', invoice.type),
                                ('reference', '=', invoice.reference),
                                ('company_id', '=', invoice.company_id.id), 
                                ('commercial_partner_id', '=', invoice.commercial_partner_id.id), 
                                ('amount_untaxed', '=', invoice.amount_untaxed),
                                ('date_invoice', '=', invoice.date_invoice),
                                ('id', '!=', invoice.id)]):
                    raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/credit note."))

class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    num_purchase = fields.Char('Nº Order')
