# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields,_, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    
    def _get_group_quants(self):
        location_id = self.origin_location_id.id
        company = self.env['res.company']._company_default_get(
            'stock.inventory',
        )
        # Using sql as search_group doesn't support aggregation functions
        # leading to overhead in queries to DB
        query = """
            SELECT product_id, lot_id, SUM(quantity)
            FROM stock_quant
            WHERE location_id = %s
            AND company_id = %s
            GROUP BY product_id, lot_id
            limit 250
        """
        self.env.cr.execute(query, (location_id, company.id))
        return self.env.cr.dictfetchall()
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
        



