# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, _


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def chekc_fpos_vies_vat(self):
        for partner in self:
            fp_prev = partner.property_account_position_id
            if partner.country_id:
                fiscal_position_id = self.env[
                    "account.fiscal.position"
                ]._get_fpos_by_region(partner.country_id.id, False, False, True)
                if fiscal_position_id:
                    if fiscal_position_id.check_vies:
                        partner.check_vat()
                        if not partner.vies_passed:
                            return "NOT VIES"
                        else:
                            return fiscal_position_id.id
                    else:
                        return fiscal_position_id.id
                return fp_prev and fp_prev.id or False

    @api.onchange("country_id", "vat")
    def on_change_check_vies(self):
        fp_id = self.chekc_fpos_vies_vat()
        res = {}
        if fp_id == "NOT VIES":
            res["warning"] = {
                "title": _("Warning for %s") % self.name,
                "message": "Vies not valid",
            }
        else:
            self.property_account_position_id = fp_id
        return res
