# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = ["product.product", "model.incident.base"]
    _name = "product.product"
