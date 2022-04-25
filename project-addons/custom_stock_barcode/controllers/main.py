# © 2022 Comunitea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController

class SplitProductLine(http.Controller):

    @http.route(['/custom_stock_barcode/button_split_product_line'], type='json', auth="public", website=True)
    def button_split_product_line(self, **kwargs):
        if not kwargs or "move_line_id" not in kwargs or "product_uom_qty" not in kwargs:
            return False
        move_line_id = request.env["stock.move.line"].browse(int(kwargs['move_line_id']))

        move_line_id.update({
            'qty_done': move_line_id.product_uom_qty - int(kwargs['product_uom_qty']),
        })
        move_id = move_line_id.move_id
        move_id.move_line_ids.filtered(lambda x: x.qty_done == 0).unlink()
        for sml_id in move_id.move_line_ids:
            sml_id.product_uom_qty = sml_id.qty_done
        move_id._recompute_state()

        ctx = request.env.context.copy()
        if move_id.product_id.tracking != 'none':
            ctx.update(not_lot_id = move_id.move_line_ids.mapped('lot_id'))
        else:
            ctx.update(not_loc_id = move_id.move_line_ids.mapped('location_id'))
        move_id.with_context(ctx)._action_assign()

        if move_line_id.product_uom_qty != move_line_id.qty_done:
            return False
        return True

    
    @http.route(['/custom_stock_barcode/button_split_incoming_product_line'], type='json', auth="public", website=True)
    def button_split_incoming_product_line(self, **kwargs):
        if not kwargs or "move_line_id" not in kwargs or "product_uom_qty" not in kwargs:
            return False
        move_line_id = request.env["stock.move.line"].browse(int(kwargs['move_line_id']))

        move_line_id.update({
            'qty_done': move_line_id.product_uom_qty - int(kwargs['product_uom_qty']),
        })
        move_id = move_line_id.move_id
        move_id.move_line_ids.filtered(lambda x: x.qty_done == 0).unlink()
        for sml_id in move_id.move_line_ids:
            sml_id.product_uom_qty = sml_id.qty_done
        move_id._recompute_state()

        move_id._action_assign()
        return True

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
