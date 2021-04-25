# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = ["purchase.order", "model.incident.base"]
    _name = "purchase.order"
