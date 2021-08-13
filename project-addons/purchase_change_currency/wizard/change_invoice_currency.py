# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ChangeInvoiceCurrency(models.TransientModel):
    _name = 'change.invoice.currency'

    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    rate = fields.Float("Rate", digits=(16, 6) , help='Rate conversion: 1 Invoice Currency  = rate x this currency', default=1.0)


    def change_currency(self):
        context = self.env.context
        invoice = self.env['account.invoice'].browse(context['active_id'])
        invoice.currency_id = self.currency_id
        for line in invoice.invoice_line_ids:
            line.price_unit =  line.price_unit * self.rate
        return True
