# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PrestashopProductTemplate(models.Model):
    _inherit = "prestashop.product.template"

    out_of_stock = fields.Selection(default="2")
