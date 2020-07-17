# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def bypass_vies_fpos_check(self):
        self.ensure_one()
        if not self.commercial_partner_id.vat and not self.commercial_partner_id.property_account_position_id:
            return True
        return False

    def action_invoice_open(self):
        for invoice in self:
            if (
                invoice.fiscal_position_id
                and not invoice.bypass_vies_fpos_check()
            ):
                res_vies = invoice.partner_id.chekc_fpos_vies_vat()
                if res_vies == "NOT VIES":
                    raise ValidationError(
                        _("The partner %s has not passed VIES validation.")
                        % invoice.partner_id.name
                    )
                    return False
        res = super().action_invoice_open()
        return res
