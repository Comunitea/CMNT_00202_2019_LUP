# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class AccountInvoice(models.Model):
    _inherit = ["account.invoice", "model.incident.base"]
    _name = "account.invoice"
