# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_barcode_view_state(self):
        res = super(StockPicking, self).get_barcode_view_state()
        for pick in res:

            # Adding parent location_id/location_dest_id in move_line_ids
            for move_line_id in pick['move_line_ids']:
                if move_line_id['location_id'] and move_line_id['location_id']['id']:
                    mvl_location_id = self.env['stock.location'].browse(move_line_id['location_id']['id']).read(['location_id','posx', 'posy', 'posz',])[0]
                    if mvl_location_id and mvl_location_id['location_id'] and mvl_location_id['location_id'][0]:
                        move_line_id['location_id']['posx'] = mvl_location_id['posx']
                        move_line_id['location_id']['posy'] = mvl_location_id['posy']
                        move_line_id['location_id']['posz'] = mvl_location_id['posz']
                        move_line_id['location_id']['location_id'] = self.env['stock.location'].browse(mvl_location_id['location_id'][0]).read(['id', 'display_name',])[0]

                    mvl_location_dest_id = self.env['stock.location'].browse(move_line_id['location_dest_id']['id']).read(['location_id','posx', 'posy', 'posz',])[0]
                    if mvl_location_dest_id and mvl_location_dest_id['location_id'] and mvl_location_dest_id['location_id'][0]:
                        move_line_id['location_dest_id']['posx'] = mvl_location_dest_id['posx']
                        move_line_id['location_dest_id']['posy'] = mvl_location_dest_id['posy']
                        move_line_id['location_dest_id']['posz'] = mvl_location_dest_id['posz']
                        move_line_id['location_dest_id']['location_id'] = self.env['stock.location'].browse(mvl_location_dest_id['location_id'][0]).read(['id', 'display_name',])[0]

            # Adding parent location_id/location_dest_id in pickings
            if pick['location_id'] and pick['location_id']['id']:
                parent_location_id = self.env['stock.location'].browse(pick['location_id']['id']).read(['location_id','posx', 'posy', 'posz',])[0]
                if parent_location_id and parent_location_id['location_id'] and parent_location_id['location_id'][0]:
                    pick['location_id']['posx'] = parent_location_id['posx']
                    pick['location_id']['posy'] = parent_location_id['posy']
                    pick['location_id']['posz'] = parent_location_id['posz']
                    plocation_id = parent_location_id['location_id'][0]
                    pick['location_id']['location_id'] = self.env['stock.location'].browse(plocation_id).read(['id', 'display_name',])[0]
            
            if pick['location_dest_id'] and pick['location_dest_id']['id']:
                parent_location_dest_id = self.env['stock.location'].browse(pick['location_dest_id']['id']).read(['location_id','posx', 'posy', 'posz',])[0]
                if parent_location_dest_id and parent_location_dest_id['location_id'] and parent_location_dest_id['location_id'][0]:
                    pick['location_dest_id']['posx'] = parent_location_dest_id['posx']
                    pick['location_dest_id']['posy'] = parent_location_dest_id['posy']
                    pick['location_dest_id']['posz'] = parent_location_dest_id['posz']
                    plocation_dest_id = parent_location_dest_id['location_id'][0]
                    pick['location_dest_id']['location_id'] = self.env['stock.location'].browse(plocation_dest_id).read(['id', 'display_name',])[0]
        return res