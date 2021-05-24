# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class PrestashopBackend(models.Model):
    _inherit = "prestashop.backend"

    @api.multi
    def import_products(self):
        for backend_record in self:
            self.env['prestashop.product.combination.option.value'].with_delay().import_batch(backend_record)
        return super().import_products()
