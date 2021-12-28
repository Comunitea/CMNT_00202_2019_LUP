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


class ProductTemplateImporter(Component):
    _inherit = 'prestashop.product.template.importer'
    
    def attribute_line(self, binding):
        self.env['product.template.attribute.line'].search(
            [('product_tmpl_id', '=', binding.odoo_id.id)]).unlink()
        template_id = binding.odoo_id.id
        products = self.env['product.product'].search([
            ('product_tmpl_id', '=', template_id)]
        )
        if products:
            attribute_ids = []
            for product in products:
                for attribute_value in product.attribute_value_ids:
                    attribute_ids.append(attribute_value.attribute_id.id)
                    # filter unique id for create relation
            for attribute_id in set(attribute_ids):
                values = products.mapped('attribute_value_ids').filtered(
                    lambda x: (x.attribute_id.id == attribute_id))
                if values:
                    self.env['product.template.attribute.line'].create({
                        'attribute_id': attribute_id,
                        'product_tmpl_id': template_id,
                        'value_ids': [(6, 0, values.ids)],
                    })
