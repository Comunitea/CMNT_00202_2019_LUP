# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields,_, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def apply_pick_putaway_strat(self):
       
        for pick in self:
            strategy_id = pick.move_dest_id.putaway_strategy_id
            for sml in pick.move_line_ids:
                domain = [('product_id', '=', sml.product_id.id), ('putaway_id', '=', strategy_id.id)]
                p_id = self.env['stock.fixed.putaway.strat'].search(domain, limit=1)
                if p_id:
                    sml.location_dest_id = p_id.fixed_location_id.id


