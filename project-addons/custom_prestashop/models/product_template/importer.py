# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class TemplateMapper(Component):
    _inherit = "prestashop.product.template.mapper"

    @mapping
    def taxes_id(self, record):
        taxes = self._get_tax_ids(record)
        if taxes:
            return {'taxes_id': [(6, 0, taxes.ids)]}

    @mapping
    def barcode(self, record):
        if self.has_combinations(record):
            return {}
        barcode = record.get('barcode') or record.get('ean13')
        if barcode in ['', '0']:
            return {}
        return {'barcode': barcode}
