# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SaleOrderImporter(Component):
    _inherit = "prestashop.sale.order.importer"

    def _has_to_skip(self):
        """ Return True if the import can be skipped """
        if self._get_binding():
            ps_state_id = self.prestashop_record["current_state"]
            state = self.binder_for("prestashop.sale.order.state").to_internal(
                ps_state_id, unwrap=1
            )
            self._get_binding().prestashop_state = state.id
        return super()._has_to_skip()


class SaleOrderImportMapper(Component):
    _inherit = 'prestashop.sale.order.mapper'

    @mapping
    def company_id(self, record):
        return {'company_id': self.backend_record.company_id.id}
