# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"
    need_export_stock = fields.Boolean()

    @api.multi
    def update_prestashop_qty(self):
        if self._context.get("cron_compute"):
            self.write({"need_export_stock": False})
            return super().update_prestashop_qty()
        else:
            self.write({"need_export_stock": True})
