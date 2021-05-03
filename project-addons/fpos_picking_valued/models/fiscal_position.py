# © 2021 Comunitea 
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    valued_picking = fields.Boolean(
        string="Valued picking",
        help="Establish valued picking in partner",
    )

