# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     result = super().onchange_product_id()
    #     if self.product_id and self.product_id.seller_ids and \
    #             self.order_id and self.order_id.partner_id:
    #         sell_lines = self.product_id.seller_ids.filtered(
    #             lambda x: x.name.id == self.partner_id.id)
    #         if sell_lines and sell_lines[0].name:
    #             result['name'] = '['
    #     return result