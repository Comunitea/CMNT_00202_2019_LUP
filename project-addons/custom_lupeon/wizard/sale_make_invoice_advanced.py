# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    @api.multi
    def create_invoices(self):
        """
        No invoice if customer ref PENDIENTE
        """
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        for order in sale_orders:
            if order.partner_id.require_num_order and \
                    order.client_order_ref == 'PENDIENTE':
                raise UserError(_(\
                    'Can not create invoice if client order ref is PENDIENTE'))
        res = super().create_invoices()

        projects = sale_orders.filtered(lambda s: s.invoice_status == 'invoiced').mapped('project_id')
        if projects:
            projects.active = False
            projects.mapped('task_ids').write({'active': True})
        return res
