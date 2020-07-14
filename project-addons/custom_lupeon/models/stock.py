# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import models, fields, api, _


class StockMove(models.Model):

    _inherit = "stock.move"

    line_state = fields.Selection(related='sale_line_id.state', 
        string="State sale line", store=True)
    
    
class PickingType(models.Model):

    _inherit = "stock.picking.type"


    def _compute_picking_count(self):
        # SE SOBREESCRIBE
        domains = {
            'count_picking_draft': [('state', '=', 'draft'), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting')), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_ready': [('state', '=', 'assigned'), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed')), ('sale_id.state','not in', ['draft', 'sent'])],
            'count_picking_late': [('scheduled_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                    ('state', 'in', ('assigned', 'waiting', 'confirmed')),
                                    ('sale_id.state','not in', ['draft', 'sent'])],
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

   