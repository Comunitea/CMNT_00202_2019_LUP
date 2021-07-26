# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('state', 'order_line.invoice_status', 'order_line.invoice_lines',
                 'order_line.is_delivery', 'order_line.is_downpayment')
    def _get_invoiced(self):
        super(SaleOrder, self)._get_invoiced()
        for order in self:
            order_line = order.order_line.filtered(lambda x: not x.is_delivery and not x.product_id.invoice_with_products and not x.is_downpayment and not x.display_type)
            if all(line.product_id.invoice_policy == 'delivery' and line.invoice_status == 'no' for line in order_line):
                order.update({'invoice_status': 'no'})
            order_line_to_invoice = order.order_line.filtered(lambda x: x.invoice_status == 'to invoice')
            if all( l.price_subtotal ==0 and l.product_id.type == 'service'  for l in order_line_to_invoice): # Si  son servicios a 0
                order.update({'invoice_status': 'invoiced'})
