# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def bypass_vies_fpos_check(self):
        res = super().bypass_vies_fpos_check()
        if self.prestashop_bind_ids:
            return True
        return res
