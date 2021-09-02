# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

class StockQuant(models.Model):

    _inherit = "stock.quant"

    
    blocked = fields.Boolean('Blocked')

    # def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
    #     res = super()._gather(
    #         product_id, location_id, lot_id=lot_id, package_id=package_id,
    #         owner_id=owner_id, strict=strict)
    #     if self._context.get('no_blocked'):
    #         return res
    #     else:
    #         return res.filtered(lambda q: not q.blocked)
