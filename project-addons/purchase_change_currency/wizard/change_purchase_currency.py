# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ChangePurchaseCurrency(models.TransientModel):
    _name = 'change.purchase.currency'

    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    rate = fields.Float("Rate", digits=(16, 6) , help='Rate conversion: 1 Purchase Currency  = rate x this currency', default=1.0)


    def change_currency(self):
        context = self.env.context
        purchase = self.env['purchase.order'].browse(context['active_id'])
        purchase.currency_id = self.currency_id
        for line in purchase.order_line:
            line.price_unit =  line.price_unit * self.rate
        return True
