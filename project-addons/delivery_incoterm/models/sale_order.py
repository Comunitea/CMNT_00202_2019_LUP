# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        for order in self:
            if order.carrier_id and order.carrier_id.incoterm:
                order.incoterm = order.carrier_id.incoterm.id
                