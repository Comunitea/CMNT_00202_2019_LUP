# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'

    check_order_validate = fields.Boolean('Permiso administración al validar')