# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def action_confirm(self):
        """
        Check if order requires client_order_ref.
        Creation of product sheet ids
        """
        for order in self:
            # Solo lupeon (al menos inicialmente para controlar lso pedidos de PS)
            if (order.company_id.id == 1 and not order.partner_d.commercial_partner_id.validated):
                raise UserError(_('Es necesario validar el cliente antes de aprobar el pedido.'))

        res = super().action_confirm()
        return res

    
