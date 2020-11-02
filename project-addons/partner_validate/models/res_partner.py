# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    validated = fields.Boolean(
        "Validated", default=False
    )
  
    @api.multi
    def toggle_validated(self):
        """ Inverse the value of the field ``validated`` on the records in ``self``. """
        for record in self:
            record.validated = not record.validated

  