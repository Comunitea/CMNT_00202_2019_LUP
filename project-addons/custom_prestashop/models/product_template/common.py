# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PrestashopProductTemplate(models.Model):
    _inherit = "prestashop.product.template"

    out_of_stock = fields.Selection(default="2")


class ProductQtyMixin(models.AbstractModel):
    _inherit = 'prestashop.product.qty.mixin'

    def _prestashop_qty(self, backend):
        qty = self[backend.product_qty_field]
        return qty
