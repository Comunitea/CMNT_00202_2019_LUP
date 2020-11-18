# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    validated = fields.Boolean(
        "Validated", default=False
    )
  
    @api.multi
    def toggle_validated(self):
        """ Inverse the value of the field ``validated`` on the records in ``self``. """
        if self.user_has_groups('partner_validate.group_sale_partner_validate'):
            for record in self:
                record.validated = not record.validated
        else:
            message = _("You cannot modify validation of partners. Check your settings or ask someone with the 'Partner Validate' role")
            raise UserError(message)

  