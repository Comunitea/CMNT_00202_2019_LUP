# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SaleOrder(models.Model):

    _inherit = "sale.order"

    report_image = fields.Binary('Report image')


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    report_tech = fields.Char('Technology')
    report_material = fields.Char('Material')
    report_finish = fields.Char('Finish')
    model_image = fields.Binary('Model image')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        """
        Cuando es producto CRP (los que se conmvierten en almacenables)
        propago los fatos de la linea de venta asociada
        """
        res = super().product_id_change()
        if self.product_id and self.product_id.sale_line_id:
            self.report_tech = self.product_id.sale_line_id.report_tech
            self.report_material = self.product_id.sale_line_id.report_material
            self.report_finish = self.product_id.sale_line_id.report_finish
            self.model_image = self.product_id.sale_line_id.model_image
        return res


    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Propagar campos a la factura
        """
        res = super()._prepare_invoice_line(qty)
        res.update({
            'report_tech': self.report_tech,
            'report_material': self.report_material,
            'report_finish': self.report_finish,
            'model_image': self.model_image,
            'ref': self.ref
        })
        return res
