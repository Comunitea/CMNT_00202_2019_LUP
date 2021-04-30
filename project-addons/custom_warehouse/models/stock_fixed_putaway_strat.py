# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields,_, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    @api.multi
    def group_lines(self):
        lines_grouped = {}
        for line in self.stock_move_location_line_ids:
            lines_grouped.setdefault(
                line.product_id.id,
                self.env["wiz.stock.move.location.line"].browse(),
            )
            lines_grouped[line.product_id.id] |= line
        return lines_grouped

    def _get_group_quants(self):
        return super()._get_group_quants()

class StockFixedPutawayStrat(models.Model):

    _inherit = "stock.fixed.putaway.strat"

    
    """
        DELETE FROM stock_fixed_putaway_strat T1
        USING   stock_fixed_putaway_strat T2
        WHERE   
        T1.id < T2.id 
        and T1.product_id  = T2.product_id 
        and T1.fixed_location_id = T2.fixed_location_id
        and T1.putaway_id = T2.putaway_id;
    """
        



