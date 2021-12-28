# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.tools.misc import formatLang


class PurchaseOrder(models.Model):
    _inherit="purchase.order"

    @api.multi
    def _compute_purchased_qties(self):
        for purchase_id in self:
            order_lines = purchase_id.order_line.filtered(lambda x: x.product_id.type in ['product', 'consu'])
            purchase_id.purchased_qties = sum(x.product_uom_qty for x in order_lines)
            purchase_id.received_qties = sum(x.qty_received for x in order_lines)

    purchased_qties = fields.Float('Totat Ordered Qty', compute=_compute_purchased_qties)
    received_qties = fields.Float('Totat Received Qty', compute=_compute_purchased_qties)
    received = fields.Selection([('received', 'Received'),
                                    ('not_received', 'Not Received'),
                                    ('partially', 'Partially Received')],
                                string='Received',
                                default='not_received',
                                compute="_compute_received",
                                store=True)
    urgent = fields.Boolean('Urgente', compute="_compute_urgents" )

    def _compute_urgents(self):
        for purchase in self.filtered(lambda p: p.state in ['draft', 'sent', 'to_approve']):
            products = purchase.mapped('order_line').mapped('product_id')
            conf_p = products.filtered(lambda p: p.qty_available_confirmed < 0)
            if conf_p:
                purchase.urgent = True
            else:
                purchase.urgent = False
        self.filtered(lambda p: p.state not in ['draft', 'sent', 'to_approve']).write({'urgent': False})

    @api.depends('picking_ids.state')
    def _compute_received(self):
        for order in self:
            if order.picking_ids:
                if all([x.state in ['done', 'cancel'] for x in order.picking_ids]):
                    order.received = 'received'
                elif any([x.state in ['done'] for x in order.picking_ids]):
                    order.received = 'partially'
                else:
                    order.received = 'not_received'
            else:
                order.received = 'not_received'


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    check = fields.Boolean('Check')
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




