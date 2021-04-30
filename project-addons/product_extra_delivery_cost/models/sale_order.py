# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"


    def get_delivery_price(self):
        super().get_delivery_price()
        for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
            if order.delivery_rating_success:
                so_lines = order.order_line.filtered(lambda x: x.product_id.delivery_extra_cost)
                if so_lines:
                    extra_price = sum(so_lines.mapped('product_id').mapped('delivery_extra_cost'))
                    order.delivery_price += extra_price
                    if not order.delivery_message:
                        order.delivery_message = "\n Se ha aplicado un coste extra de {} ".format(extra_price)
                    else:
                        order.delivery_message += "\n Se ha aplicado un coste extra de {}".format(extra_price)

                           