# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class PrestashopTrackingExporter(Component):
    _inherit = 'prestashop.stock.tracking.exporter'

    def run(self, binding, **kwargs):
        pass


class PrestashopStockPickingListener(Component):
    _inherit = 'prestashop.stock.picking.listener'

    def on_tracking_number_added(self, record):
        return
