# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.tools.misc import formatLang




class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

   
    product_categ_id = fields.Many2one(
        "product.category", "Category", related="product_id.categ_id"
    )
    to_deliver_qty = fields.Float(compute="_compute_to_deliver_qty")
    
    

    def _compute_to_deliver_qty(self):
        ## Todo revisar con Jose Luis que movimientos se tienen en cuenta.
        domain = [
                  ('location_id.usage', '=', 'internal'),
                  ('location_dest_id.usage', '!=', 'internal'),
                  ('state', 'in', ('partially_available', 'assigned', 'confirmed')),
                  ('product_id', 'in', self.mapped('product_id').ids)]

        if self._context.get('location'):
            domain += [('location_id', 'child_of', self._context.get('location'))]

        res = self.env['stock.move'].read_group(domain, ['product_uom_qty'], ['product_id'])
        qties = {}
        for x in res:
            qties[x['product_id'][0]] = x['product_uom_qty']

        for line in self:
            product_id = line.product_id.id
            if product_id in qties.keys():
                line.to_deliver_qty = qties[line.product_id.id]
            else:
                line.to_deliver_qty = 0
        return

        for line in self:
            self.env.cr.execute(
                """
                    SELECT SUM(qty_pending)
                    FROM sale_order_line
                    WHERE state not in ('draft','sent', 'cancel') AND
                    product_id={}
                """.format(
                    line.product_id.id
                )
            )
            result = self.env.cr.fetchone()
            if result and result[0]:
                line.to_deliver_qty = result[0]
            else:
                line.to_deliver_qty = 0




