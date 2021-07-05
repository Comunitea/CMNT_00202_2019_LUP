# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP



class StockPicking(models.Model):

    _inherit = "stock.picking"

    warn_msg = fields.Text(compute="_compute_warns")
    warn = fields.Selection(WARNING_MESSAGE, 'Avisos', help=WARNING_HELP, 
                            compute="_compute_warns",
                            store=True)
    
    @api.depends('partner_id')
    def _compute_warns(self):
        for obj in self:
            if obj.partner_id.picking_warn != 'no-message':
                obj.warn = obj.partner_id.picking_warn
                obj.warn_msg = obj.partner_id.picking_warn_msg
            else:
                obj.warn = obj.partner_id.commercial_partner_id.picking_warn
                obj.warn_msg = obj.partner_id.commercial_partner_id.picking_warn_msg