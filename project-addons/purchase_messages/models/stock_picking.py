# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
#from odoo.exceptions import RedirectWarning, UserError, ValidationError



class StockPicking(models.Model):

    _inherit = "stock.picking"


    @api.multi
    def _compute_messages_ids(self):
        for pick in self:
            pick_messages = pick.sale_id.mapped('order_message_ids').filtered(lambda r: r.picking_available)
            p_pick_messages = pick.purchase_id.mapped('order_message_ids').filtered(lambda r: r.picking_available)
            pick.sale_message_ids = pick_messages.ids + p_pick_messages.ids
            pick.sale_message_count = len(pick.sale_message_ids)
    
