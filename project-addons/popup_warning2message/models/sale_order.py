# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP



class SaleOrder(models.Model):

    _inherit = "sale.order"

    warn_msg = fields.Text(compute="_compute_warns", store=True)
    warn = fields.Selection(WARNING_MESSAGE, 'Avisos',
                            help=WARNING_HELP,
                            compute="_compute_warns",
                            store=True)
    
    @api.depends('partner_id')
    def _compute_warns(self):
        for obj in self:
            if obj.partner_id.sale_warn != 'no-message':
                obj.warn = obj.partner_id.sale_warn
                obj.warn_msg = obj.partner_id.sale_warn_msg
            else:
                obj.warn = obj.partner_id.commercial_partner_id.sale_warn
                obj.warn_msg = obj.partner_id.commercial_partner_id.sale_warn_msg