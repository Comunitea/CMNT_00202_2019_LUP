# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)


class StockMoveLine (models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def unlink_stock_move (self):
        for sml in self:
            sml.unlink()

    @api.multi
    def check_move_availability(self):
        for sml in self.filtered(lambda x: x.state not in ('done', 'assigned')):
            sml.move_id._action_assign()

    sale_id = fields.Many2one(related="picking_id.sale_id")
    partner_id = fields.Many2one(related="sale_id.partner_id", readonly=True, store=True)
    date_order = fields.Datetime(related="sale_id.date_order", readonly=True, store=True)
    state_order = fields.Selection(related="sale_id.state", readonly=True, store=True, string="Estado pedido")
    mail_supplier = fields.Char(related='product_id.variant_seller_ids.name.email', readonly=True, store=True, string = "Correo prov.")


    @api.multi
    def action_open_picking_id(self):

        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['view_mode'] = 'form'
        del action['views']
        del action['view_id']
        action['res_id'] = self.picking_id.id
        return action

    @api.multi
    def action_open_sale_id(self):
        if self.sale_id:
            action = self.env.ref('sale.action_orders').read()[0]
            action['view_mode'] = 'form'
            del action['views']
            del action['view_id']
            action['res_id'] = self.sale_id.id
            return action

            action = self.env.ref('account.action_move_journal_line').read()[0]

        return action




class StockQuant(models.Model):
    _inherit = "stock.quant"


    def action_view_stock_moves_reservations(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [
            ('state', 'in', ['assigned', 'partially_available']),
            ('product_id', '=', self.product_id.id),
            '|',
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            '|',
                ('package_id', '=', self.package_id.id),
                ('result_package_id', '=', self.package_id.id),
        ]
        action['context'] = {'search_default_todo': 1,
                             'search_default_by_state': 1}
        action['view_id'] = self.env.ref('quant_picking_rel.view_move_line_quant_link').id
        action['views'][0] = (action['view_id'], 'tree')
        return action
