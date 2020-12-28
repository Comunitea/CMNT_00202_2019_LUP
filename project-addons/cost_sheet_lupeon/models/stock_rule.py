# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        res = super()._run_manufacture(product_id, product_qty, product_uom, location_id, name, origin, values)
        product = product_id
        if product.group_sheet_id:
            mrp_types = ['fdm', 'sls', 'poly', 'sla', 'sls2', 'dmls']
            for sheet in product.group_sheet_id.sheet_ids.filtered(
                    lambda sh: sh.sheet_type in mrp_types):
                bom = sheet.production_id and sheet.production_id.bom_id
                vals = {
                    'sheet_id': sheet.id,
                    'sale_line_id': sheet.sale_line_id.id,
                    # 'sale_id': sheet.sale_line_id.order_id.id,
                    'product_id': sheet.product_id.id,
                    'product_uom_id': sheet.product_id.uom_id.id,
                    'product_qty': sheet.cus_units,  # TODO get_qty,
                    'bom_id': bom.id,
                    'date_planned_start': datetime.now() + timedelta(days=1),
                    # 'line_ref': sheet.sale_line_id.ref,
                    'date_planned_finished':
                    # sheet.sale_line_id.order_id.production_date or False,
                    datetime.now() + timedelta(days=3),
                    'repeated_mrp': sheet.sale_line_id.ref,
                    # 'line_ref': sheet.sale_line_id.ref,
                    # 'line_name': sheet.sale_line_id.name,
                }
                prod = self.env['mrp.production'].create(vals)
                prod.onchange_product_id()
                prod.action_assign()
                prod.button_plan()
                # sheet.update_workorders(prod)
        return res
