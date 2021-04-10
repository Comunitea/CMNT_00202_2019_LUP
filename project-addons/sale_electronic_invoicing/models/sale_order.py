# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    eic = fields.Boolean('Pedido con facturación electrónica',default=False)


    @api.onchange('eic')
    def _onchange_eic(self):
        if self.eic:
            self.invoice_policy = 'order'
            self.delivery_blocked = True
            self.payment_mode_id = self.company_id.eic_payment_mode_id.id
            self.payment_term_id = self.company_id.eic_payment_term_id.id
        else:
            self.invoice_policy = 'delivery'
            self.delivery_blocked = False
            self.payment_mode_id = self.partner_id.customer_payment_mode_id.id
            self.payment_term_id = self.partner_id.property_payment_term_id.id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.eic:
            self.eic = self.partner_id.eic
