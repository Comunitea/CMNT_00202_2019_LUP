# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PartnerImportMapper(Component):
    _inherit = "prestashop.res.partner.mapper"

    @mapping
    def groups(self, record):
        return {'category_id': [(6, 0, [self.env.ref('custom_prestashop.prestashop_tag').id])]}


class ResPartnerImporter(Component):
    _inherit = "prestashop.res.partner.importer"

    def _import_dependencies(self):
        return
