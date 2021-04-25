# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = ["sale.order", "model.incident.base"]
    _name = "sale.order"
    