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

            # CREO COMPRAS, COMO LA FUNCIÓN DE VENTAS
            p_lines = product.group_sheet_id.sheet_ids.mapped(
                'purchase_line_ids').filtered(lambda x: x.partner_id)
            self._create_purchases(p_lines, product, product_qty)
        return res

    def _create_purchases(self, lines, product, product_qty):
        """
        Crea compras agrupadas por proveedor y las enlaza al aventa.
        Hay una función equivalente en stock.rule que no la enlaza al producto
        TODO refactorizar
        """
        self.ensure_one()
        suppliers = lines.mapped('partner_id')
        supplier_purchase = {}
        for partner in suppliers:
            vals = {
                'partner_id': partner.id,
                'origin': 'CRP - ' + product.name,
                'dest_sale_id': False,
                'payment_term_id':
                partner.property_supplier_payment_term_id.id,
                'date_order': fields.Datetime.now()
            }
            po = self.env['purchase.order'].create(vals)
            supplier_purchase[partner.id] = po

        for line in lines:
            po = supplier_purchase[line.partner_id.id]
            taxes = line.product_id.supplier_taxes_id
            # fpos = po.fiscal_position_id
            # taxes_id = fpos.map_tax(
            #     taxes, line.product_id.id, line.partne_id.name) if fpos \
            #     else taxes
            factor = line.qty / (line.sheet_id.cus_units or 1.0)
            qty = product_qty * factor
            vals = {
                'name': line.name or line.product_id.name,
                'product_qty': qty,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'price_unit': line.cost_ud,
                'date_planned': fields.Datetime.now(),
                # 'taxes_id': [(6, 0, taxes_id.ids)],
                'taxes_id': [(6, 0, taxes.ids)],
                'order_id': po.id,
            }
            self.env['purchase.order.line'].create(vals)