# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = ["stock.picking", "model.incident.base"]
    _name = "stock.picking"
