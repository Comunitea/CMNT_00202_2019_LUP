# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def bypass_vies_fpos_check(self):
        self.ensure_one()
        if not self.partner_id.commercial_partner_id.vat and not self.partner_id.commercial_partner_id.property_account_position_id:
            return True
        return False

    def action_confirm(self):
        for order in self:
            if order.fiscal_position_id and not order.bypass_vies_fpos_check():
                res_vies = order.partner_id.check_fpos_vies_vat()
                if res_vies == "NOT VIES":
                    raise ValidationError(
                        _("The partner %s has not passed VIES validation.")
                        % order.partner_id.name
                    )
                    return False
        res = super().action_confirm()
        return res
