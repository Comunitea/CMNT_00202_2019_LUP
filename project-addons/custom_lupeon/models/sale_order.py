# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        """
        Check if order requires client_order_ref.
        Creation of product sheet ids
        """
        for order in self:
            if (order.partner_id.require_num_order):
                order.client_order_ref = 'PENDIENTE'
        res = super().action_confirm()
        return res
    
    @api.multi
    def write(self, vals):
        """
        Propagar cambio de referencia a la factura
        """
        res = super().write(vals)
        if vals.get('client_order_ref'):
            invoices = self.mapped('invoice_ids')
            if invoices:
                invoices.write({'name': vals['client_order_ref']})
        return res

 