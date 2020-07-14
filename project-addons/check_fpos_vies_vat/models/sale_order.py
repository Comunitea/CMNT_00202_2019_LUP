# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"
    
    @api.multi
    def action_confirm(self):
        for order in self:
            if order.fiscal_position_id:
                res_vies = order.partner_id.chekc_fpos_vies_vat()
                if res_vies == "NOT VIES":
                    raise ValidationError(
                    _('The partner %s has not passed VIES validation.' % order.partner_id.name)
                )
                return False 
        res = super().action_confirm()
        return res

