# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ProductCombinationMapper(Component):
    _inherit = "prestashop.product.combination.mapper"

    @mapping
    def from_main_template(self, record):
        main_template = self.get_main_template_binding(record)
        result = super().from_main_template(record)
        if (
            main_template.get("type")
            and main_template["type"] == "virtual"
        ):
            result["type"] = "service"
        else:
            result["type"] = "product"
        return result
