# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, http
from odoo.http import request

from odoo.addons.stock_barcode.controllers.main import StockBarcodeController


class CustomStockBarcodeController(StockBarcodeController):
    @http.route("/stock_barcode/get_set_barcode_view_state", type="json", auth="user")
    def get_set_barcode_view_state(
        self, model_name, record_id, mode, write_field=None, write_vals=None
    ):
        if model_name != "mrp.production":
            return super(CustomStockBarcodeController, self).get_set_barcode_view_state(
                model_name, record_id, mode, write_field, write_vals
            )
        if mode != "read":
            request.env[model_name].browse(record_id).move_raw_ids.write(
                {write_field: write_vals}
            )
        return request.env[model_name].browse(record_id).get_barcode_view_state()
