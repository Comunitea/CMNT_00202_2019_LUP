# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError

import operator as py_operator

import logging

_logger = logging.getLogger(__name__)

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class ProductProduct (models.Model):
    _inherit = 'product.product'

    @api.multi
    def compute_reservations(self):
        res_prod = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        warehouse_id = self._context.get('warehouse_id', False)
        if not warehouse_id:
            warehouse_id = self.env['stock.warehouse'].search([], limit=1)
        else:
            warehouse_id = self.env['stock.warehouse'].browse(warehouse_id)
        loc_id = warehouse_id.lot_stock_id
        domain = [('location_id', 'child_of', loc_id.id),
                      ('product_id', 'in', self.ids),
                      ('state', 'in', ('partially_available', 'assigned', 'confirmed'))]
        moves_res = self.env['stock.move'].read_group(domain, ['product_id', 'count(id)'], ['product_id'], orderby='id')
        moves_dict = dict((item['product_id'][0], item['product_id_count']) for item in moves_res)
        domain = [('location_id', 'child_of', loc_id.id),
                      ('product_id', 'in', self.ids),
                      ('reserved_quantity', '!=', 0)]
        quant_res = self.env['stock.quant'].read_group(domain, ['product_id', 'reserved_quantity'], ['product_id'], orderby='id')
        quant_dict = dict((item['product_id'][0], item['reserved_quantity']) for item in quant_res)
        domain = [('location_id', 'child_of', loc_id.id),
                      ('product_id', '=', self.ids),
                      ('state', 'in', ('partially_available', 'assigned', 'confirmed')),
                      ('sale_line_id.state', 'in', ('sale', 'done')),
                      '|', ('sale_line_id.order_id.prestashop_state', '=', False),('sale_line_id.order_id.prestashop_state.pending_payment', '!=', True)]
        moves_reserved_res = self.env['stock.move'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id'], orderby='id')
        moves_reserved_dict = dict((item['product_id'][0], item['product_uom_qty']) for item in moves_reserved_res)

        for product in self:
            if moves_dict.get(product.id, False):
                product.quantity_reserved_link = moves_dict[product.id]
            else:
                product.quantity_reserved_link = 0.0

            if quant_dict.get(product.id, False):
                product.quantity_reserved = quant_dict[product.id]
            else:
                product.quantity_reserved = 0.0


            if moves_reserved_dict.get(product.id, False):
                quantity_reserved_confirmed = moves_reserved_dict[product.id]
            else:
                quantity_reserved_confirmed = 0
            product.quantity_reserved_confirmed = quantity_reserved_confirmed
            product.qty_available_confirmed = res_prod[product.id]['qty_available'] - quantity_reserved_confirmed


    def _search_qty_available_confirmed(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections

        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name which slows
        # down the search because of the join on the translation table to get the translated names.
        for product in self.with_context(prefetch_fields=False).search([], order='id'):
            if OPERATORS[operator](product.qty_available_confirmed, value):
                ids.append(product.id)
        return [('id', 'in', ids)]


    def action_view_stock_moves_reservations(self):
        self.ensure_one()
        warehouse_id = self._context.get(('warehouse_id'), False)
        if not warehouse_id:
            warehouse_id = self.env['stock.warehouse'].search([], limit=1)
        else:
            warehouse_id = self.env['stock.warehouse'].browse(warehouse_id)
        loc_id = warehouse_id.lot_stock_id
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [
            ('state', 'in', ['assigned', 'partially_available']),
            ('product_id', '=', self.id),
            ('location_id', 'child_of', loc_id.id),
        ]
        action['context'] = {'search_default_todo': 1}
        action['view_id'] = self.env.ref('quant_picking_rel.view_move_line_quant_link').id
        action['views'][0] = (action['view_id'], 'tree')
        return action

    quantity_reserved_link = fields.Float('Cantidad reservada (Movimientos)', compute="compute_reservations")
    quantity_reserved = fields.Float('Cantidad reservada (Quants)', compute="compute_reservations")
    quantity_reserved_confirmed = fields.Float('Cantidad reservada confirmada', compute="compute_reservations")
    qty_available_confirmed = fields.Float('Stock previsto confirmado',
                                         compute="compute_reservations",
                                         search="_search_qty_available_confirmed")

    def action_view_stock_moves_prod(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_action').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action
