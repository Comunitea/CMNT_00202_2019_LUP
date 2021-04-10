# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class ResCompany(models.Model):

    _inherit = "res.company"

    eic_payment_mode_id = fields.Many2one('account.payment.mode', "Modo de pago para facturación electrónica")
    eic_payment_term_id = fields.Many2one('account.payment.term', "Plazo de pago para facturación electrónica")

