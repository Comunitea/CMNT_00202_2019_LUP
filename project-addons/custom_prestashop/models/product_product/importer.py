# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class ProductCombinationMapper(Component):
    _inherit = "prestashop.product.combination.mapper"

    @only_create
    @mapping
    def main_template_type(self, record):
        main_template = self.get_main_template_binding(record)
        if (
            main_template
            and main_template.odoo_id["type"] == "virtual"
        ):
            return {"type":  "service"}
        else:
            return {"type":  "product"}

    @mapping
    def weight(self, record):
        combination_weight = float(record.get('weight', '0.0'))
        main_weight = self.binder_for('prestashop.product.template').to_internal(record['id_product']).weight
        weight = main_weight + combination_weight
        return {'weight': weight}

    @mapping
    def barcode(self, record):
        barcode = record.get('barcode') or record.get('ean13')
        if barcode in ['', '0']:
            backend_adapter = self.component(
                usage='backend.adapter',
                model_name='prestashop.product.template'
            )
            template = backend_adapter.read(record['id_product'])
            barcode = template.get('barcode') or template.get('ean13')
        if barcode and barcode != '0':
            return {'barcode': barcode}
        return {}


class PrestashopProductCombinationOptionValue(Component):
    _name = 'prestashop.product.combination.option.value.batch.importer'
    _inherit = 'prestashop.delayed.batch.importer'
    _apply_on = 'prestashop.product.combination.option.value'


class ProductCombinationOptionValueMapper(Component):
    _inherit = 'prestashop.product.combination.option.value.mapper'

    @only_create
    @mapping
    def odoo_id(self, record):
        return {}
