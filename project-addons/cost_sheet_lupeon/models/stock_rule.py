# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values):
        """
        En esta función se entra al disparar el abastecimiento desde la linea 
        de venta con el producto fabricación custom y al ejecutar 
        reabastecimientos.
        Esta heredada para el segundo caso, 
        cuando tenemos un producto custom que se
        ha convertido en producto almacenable desde el botón de la 
        línea de venta.
        Se crea una nueva hoja, con la lista de materiales, se espera que las
        cantidades y los tiempos sean proporcionales.
        """
        res = super()._run_manufacture(
            product_id, product_qty, product_uom, location_id, name,
            origin, values)
        product = product_id
        if product.group_sheet_id:
            mrp_types = ['fdm', 'sls', 'poly', 'sla', 'sls2', 'dmls']
            for sheet in product.group_sheet_id.sheet_ids.filtered(
                    lambda sh: sh.sheet_type in mrp_types):
                bom = sheet.production_id and sheet.production_id.bom_id
                copy_vals = {
                    'bom_id': bom.id,
                    'sale_line_id': False,
                }
                new_sheet = sheet.copy(default=copy_vals)

                # TODO get_qty, ¿Esto está bien así o solo vale si es unitario?
                qty = product_qty * sheet.cus_units

                # esto solo funciona si es unitario, que puede ser una
                # restricción
                vals = {
                    'sheet_id': new_sheet.id,
                    # 'sale_line_id': sheet.sale_line_id.id,
                    # 'sale_id': sheet.sale_line_id.order_id.id,
                    'product_id': sheet.product_id.id,
                    'product_uom_id': sheet.product_id.uom_id.id,
                    'product_qty': qty, 
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
                # Change the quantity of the production order to qty
                wiz = self.env['change.production.qty'].create(
                    {'mo_id': prod.id, 'product_qty': qty})
                wiz.change_prod_qty()
                prod.action_assign()
                prod.button_plan()
                # LO SIGUIENTE ES EQUIVALENTE A LA FUNCIÓN update_workorders DE
                # COST.SHEET
                for wo in prod.workorder_ids:
                    duration = new_sheet.machine_hours
                    oppi = new_sheet.oppi_line_ids.filtered(
                        lambda o: wo.name == o.name)
                    if oppi:
                        duration = oppi.time
                    factor = duration / wo.sheet_id.cus_units
                    duration_expected = wo.qty_production * factor
                    vals = {
                        'duration_expected': duration_expected * 60,
                        # 'date_planned_finished':
                        # self.sale_line_id.order_id.production_date,
                        # 'date_planned_start':
                        # self.sale_line_id.order_id.production_date -
                        # timedelta(hours=duration),
                    }
                    if oppi and oppi.employee_id:
                        vals.update(
                            employee_id=oppi.employee_id.id)
                    if oppi and oppi.e_partner_id:
                        vals.update(
                            e_partner_id=oppi.e_partner_id.id,)
                    wo.write(vals)

                new_sheet.write({'production_id': prod.id})
        return res
