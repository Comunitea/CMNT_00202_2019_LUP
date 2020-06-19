# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PartnerImportMapper(Component):
    _inherit = "prestashop.res.partner.mapper"

    @mapping
    def groups(self, record):
        return {'category_id': [(6, 0, [self.env.ref('custom_prestashop.prestashop_tag').id])]}

    @mapping
    def name(self, record):
        parts = [record["firstname"], record["lastname"]]
        name = " ".join(p.strip() for p in parts if p.strip())
        return {"name": record.get('company') or name}


class ResPartnerImporter(Component):
    _inherit = "prestashop.res.partner.importer"

    def _import_dependencies(self):
        return


class AddressImportMapper(Component):
    _inherit = "prestashop.address.mappper"

    @mapping
    def groups(self, record):
        return {'category_id': [(6, 0, [self.env.ref('custom_prestashop.prestashop_tag').id])]}


class AddressImporter(Component):
    _inherit = "prestashop.address.importer"

    def _after_import(self, binding):
        record = self.prestashop_record
        vat_number = None
        if record["vat_number"]:
            vat_number = record["vat_number"].replace(".", "").replace(" ", "")
        # TODO move to custom localization module
        elif not record["vat_number"] and record.get("dni"):
            vat_number = (
                record["dni"].replace(".", "").replace(" ", "").replace("-", "")
            )
        if vat_number:
            if self._check_vat(vat_number, binding.parent_id.country_id):
                binding.parent_id.write({"vat": vat_number})
