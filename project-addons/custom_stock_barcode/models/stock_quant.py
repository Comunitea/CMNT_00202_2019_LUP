# © 2022 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        quants_to_end = self.env['stock.quant']
        ## We need to put the original location in the last place of the quants list in order to allways find quantities
        quants = super(StockQuant, self)._gather(product_id=product_id, location_id=location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        not_lot_id = self._context.get('not_lot_id', False) 
        not_loc_id = self._context.get('not_loc_id', False)
        if not_lot_id:
            quants_to_end += quants.filtered(lambda x: x.lot_id in not_lot_id)
        if not_loc_id:
            quants_to_end += quants.filtered(lambda x: x.location_id in not_loc_id)
        if quants_to_end:
            quants -= quants_to_end
            quants += quants_to_end
        return quants
