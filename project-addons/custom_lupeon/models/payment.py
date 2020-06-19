# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class AccountPaymentMode(models.Model):

    _inherit = "account.payment.mode"

    payment_cost = fields.Float(string='Payment Mode Cost', default=0.0)