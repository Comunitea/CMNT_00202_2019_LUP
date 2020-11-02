# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import split_every

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):

    _inherit = "stock.move"

    line_state = fields.Selection(related='sale_line_id.state', 
        string="State sale line", store=True)
    
    
class PickingType(models.Model):

    _inherit = "stock.picking.type"


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

    delivered = fields.Boolean('Delivered', compute="_compute_delivered", store=True, readonly=False)
    delivery_blocked = fields.Boolean('Delivery blocked', related='sale_id.delivery_blocked')
    partner_phone = fields.Char('Phone', related='partner_id.phone')
    partner_mobile = fields.Char('Mobile', related='partner_id.mobile')
    partner_email = fields.Char('Email', related='partner_id.email')
    
    
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
        domain = self.env['procurement.group']._get_moves_to_assign_domain(self.company_id.id)
        #domain.append(('company_id', '=', self.company_id.id))
        moves_to_assign = self.env['stock.move'].search(domain, limit=None,
            order='priority desc, date_expected asc')
        for moves_chunk in split_every(100, moves_to_assign.ids):
            self.env['stock.move'].browse(moves_chunk)._action_assign()
            
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