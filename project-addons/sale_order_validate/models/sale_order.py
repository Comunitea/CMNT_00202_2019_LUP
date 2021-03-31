# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        """
        Check if order partner supping is complete.
        """
        for order in self:
            
            if (not order.partner_shipping_id.country_id or 
                not order.partner_shipping_id.state_id or 
                not (order.partner_shipping_id.mobile or order.partner_shipping_id.phone) or
                not order.partner_shipping_id.zip):
                raise UserError(_('No están informados todos los campos necesarios de la dirección de entrega. Por favor revise: País, provincia, código postal y teléfono'))

        res = super().action_confirm()
        return res    
