# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import split_every

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    company_id = fields.Many2one('res.company', 'Company',
                                 related='location_id.company_id',
                                 store=True)

class StockMove(models.Model):

    _inherit = "stock.move"

    line_state = fields.Selection(related='sale_line_id.state', 
        string="State sale line", store=True)
    
    
class PickingType(models.Model):

    _inherit = "stock.picking.type"

    count_picking_blocked = fields.Integer(
        compute='_compute_picking_count')

    def _compute_picking_count(self):
        # SE SOBREESCRIBE
        
        domains = {
            'count_picking_draft': [('state', '=', 'draft'), '|', 
                                    ('picking_type_id.code', '!=', 'outgoing'),
                                     '&', ('picking_type_id.code', '=', 'outgoing'), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting')), 
                                      '|', ('picking_type_id.code', '!=', 'outgoing'), 
                                      '&', ('picking_type_id.code', '=', 'outgoing'), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_ready': [('state', '=', 'assigned'), 
                                    '|', '|', ('picking_type_id.code', '!=', 'outgoing'),
                                    ('sale_id', '=', False), 
                                     '&', '&','&', ('picking_type_id.code', '=', 'outgoing'), ('sale_id.state','not in', ['draft', 'sent']), ('delivery_blocked','!=', True), 
                                     '|', ('sale_id.prestashop_state.pending_payment', '!=', True), ('sale_id.prestashop_state', '=', False)],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed')),
                               '|', ('picking_type_id.code', '!=', 'outgoing'), 
                               '&', ('picking_type_id.code', '=', 'outgoing'), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_late': [('scheduled_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                    ('state', 'in', ('assigned', 'waiting', 'confirmed')),
                                    '|', ('picking_type_id.code', '!=', 'outgoing'), 
                                    '&', ('picking_type_id.code', '=', 'outgoing'), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
            'count_picking_blocked': [('state', 'in', ('confirmed', 'assigned', 'waiting')),
                                    ('delivery_blocked','=', True)
                                    ],
        }
        for field in domains:
            data = self.env['stock.picking'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)
        for record in self:
            record.rate_picking_late = record.count_picking and record.count_picking_late * 100 / record.count_picking or 0
            record.rate_picking_backorders = record.count_picking and record.count_picking_backorders * 100 / record.count_picking or 0

   
class StockPicking(models.Model):

    _inherit = "stock.picking"

    ship_cost = fields.Monetary(string='Ship Cost', default=0.0)
    ship_price = fields.Monetary('Envio cobrado', related='sale_id.ship_price')
    delivered = fields.Boolean('Delivered', compute="_compute_delivered", store=True, readonly=False)
    delivery_blocked = fields.Boolean('Delivery blocked', compute="_compute_delivery_blocked", store=True, readonly=True)
    force_delivery_blocked = fields.Boolean('Block delivery', default=False)
    partner_phone = fields.Char('Phone', related='partner_id.phone')
    partner_mobile = fields.Char('Mobile', related='partner_id.mobile')
    partner_email = fields.Char('Email', related='partner_id.email')
    available_deliveries_ids = fields.Many2many('delivery.carrier', compute="_compute_available_deliveries", store=True)

    
    @api.depends('sale_id.delivery_blocked', 'force_delivery_blocked')
    def _compute_delivery_blocked(self):
        for pick in self:
            if pick.sale_id.delivery_blocked:
                pick.delivery_blocked = True
            else:
                if pick.force_delivery_blocked:
                    pick.delivery_blocked = True
                else:
                    pick.delivery_blocked = False

    @api.depends('partner_id')
    def _compute_available_deliveries(self):
        for picking in self:
            domain = [('ps_sync', '=', False)]
            if picking.partner_id:
                country_id = picking.partner_id.country_id.id
                state_id = picking.partner_id.state_id.id
                
                if state_id:
                    domain += [
                        '|',
                        ('state_ids', '=', False),
                        ('state_ids', '=', state_id)]
                   
                if country_id:
                    domain += [
                        '|',
                        ('country_ids', '=', False),
                        ('country_ids', '=', country_id)]

            carrier_ids = self.env['delivery.carrier'].search(domain).ids
            picking.available_deliveries_ids = carrier_ids

    @api.multi
    def do_print_picking(self):
        self.write({'printed': True})
        return self.env.ref('stock.action_report_delivery').report_action(self)

    @api.depends('sale_id.prestashop_state')
    def _compute_delivered(self):
        for picking in self:
            if picking.delivered != True and picking.sale_id.prestashop_state.trigger_delivered == True:
                picking.delivered = True

    @api.multi
    def action_done(self):
        res = super().action_done()
        # Search all confirmed stock_moves and try to assign them
        domain = self.env['procurement.group']._get_moves_to_assign_domain(
            self.company_id.id)

        #domain.append(('raw_material_production_id', '!=', False))
        moves_to_assign = self.env['stock.move'].search(domain, limit=None,
            order='priority desc, date_expected asc')
        for moves_chunk in split_every(100, moves_to_assign.ids):
            self.env['stock.move'].browse(moves_chunk)._action_assign()

        # COMPUTE LAUNCH ACTION ASSIGN FOR PRODUCTION MOVES ONLY LUPEON COMPANY:
        # No es necesario porque ya se hace globalmente, pero esto sería el código
        # para hacer la busqueda de movimientos de producciones, producto a producto
        # if self.company_id and not self.company_id.cost_sheet_sale:
        #     for product in self.move_line_ids.mapped('product_id'):
        #         domain = [
        #             ('product_id', '=', product.id),
        #             ('company_id', '=', self.company_id.id),
        #             ('state', 'in', ['confirmed', 'partially_available']),
        #             ('product_uom_qty', '!=', 0.0),
        #             ('raw_material_production_id', '!=', False)
        #         ]
        #         moves_to_assign = self.env['stock.move'].search(domain, limit=None,
        #             order='priority desc, date_expected asc')
        #         for moves_chunk in split_every(100, moves_to_assign.ids):
        #             self.env['stock.move'].browse(moves_chunk)._action_assign()

        # Merge duplicated quants
        self.env['stock.quant']._merge_quants()
        self.env['stock.quant']._unlink_zero_quants()
        return res

    def button_validate(self):
        if self.delivery_blocked:
            raise ValidationError(_(
                    'The picking is blocked form Sale Order %s') % self.sale_id.name)
        res = super().button_validate()
        return res

    @api.multi
    def action_barcode_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''

        if len(self) == 1:
            return self.open_picking_client_action()
        else:
            pt = self.mapped('picking_type_id')
            if pt:
                res = pt[0].get_action_picking_tree_ready_kanban()
                res['context'] = ('{\n'
                    "            'form_view_initial_mode': 'edit',\n"
                    "            'search_default_picking_type_id': [%s],\n"
                    "            'default_picking_type_id': %s,\n"
                    "            'contact_display': 'partner_address',\n"
                    "            'search_default_available': 1,\n"
                    "            'force_detailed_view': True,\n"
                    '        }' % (pt.id, pt.id)
                )
                res['domain'] = [('id', 'in', self.ids)]

            return res
        raise UserError(_('No pickings in assigned state to open'))
        return
    
    @api.multi
    def action_open_form(self):
        
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        
        form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.id
        return action



class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    @api.multi
    def name_get(self):
        """
        Para que se vea la descripción en la ventana de código de barras.
        Se usa display_name en la funcion get_barcode_view_state
        """
        result = []
        for ml in self:
            p_name = ml.product_id.display_name
            description = ml.move_id.name
            result.append((ml.id, '%s  (%s)' % (p_name, description)))
        return result
