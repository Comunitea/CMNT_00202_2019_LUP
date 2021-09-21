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
                    mvl_location_id = self.env['stock.location'].browse(move_line_id['location_id']['id']).read(['location_id'])[0]
                    if mvl_location_id and mvl_location_id['location_id'] and mvl_location_id['location_id'][0]:
                        mov_loc_id_parent = self.env['stock.location'].browse(mvl_location_id['location_id'][0])
                        move_line_id['location_id']['location_id'] = mov_loc_id_parent.read(['id', 'display_name', 'loc_format', 'location_id'])[0]

                        if mov_loc_id_parent and mov_loc_id_parent.location_id:
                            mov_loc_id_gparent = mov_loc_id_parent.location_id
                            move_line_id['location_id']['location_id']['location_id'] = mov_loc_id_gparent.read(['display_name'])[0]

                    mvl_location_dest_id = self.env['stock.location'].browse(move_line_id['location_dest_id']['id']).read(['location_id'])[0]
                    if mvl_location_dest_id and mvl_location_dest_id['location_id'] and mvl_location_dest_id['location_id'][0]:
                        mov_loc_id_parent_dest = self.env['stock.location'].browse(mvl_location_dest_id['location_id'][0])
                        move_line_id['location_dest_id']['location_id'] = mov_loc_id_parent_dest.read(['id', 'display_name', 'loc_format', 'location_id'])[0]

                        if mov_loc_id_parent_dest and mov_loc_id_parent_dest.location_id:
                            mov_loc_id_gparent_dest = mov_loc_id_parent_dest.location_id
                            move_line_id['location_dest_id']['location_id']['location_id'] = mov_loc_id_gparent_dest.read(['display_name'])[0]

            # Adding parent location_id/location_dest_id in pickings
            if pick['location_id'] and pick['location_id']['id']:
                parent_location_id = self.env['stock.location'].browse(pick['location_id']['id']).read(['location_id'])[0]
                if parent_location_id and parent_location_id['location_id'] and parent_location_id['location_id'][0]:

                    plocation_id = self.env['stock.location'].browse(parent_location_id['location_id'][0])
                    pick['location_id']['location_id'] = plocation_id.read(['id', 'display_name', 'loc_format', 'location_id'])[0]

                    if plocation_id and plocation_id.location_id:
                        gplocation_id = plocation_id.location_id
                        pick['location_id']['location_id']['location_id'] = gplocation_id.read(['display_name'])[0]
            
            if pick['location_dest_id'] and pick['location_dest_id']['id']:
                parent_location_dest_id = self.env['stock.location'].browse(pick['location_dest_id']['id']).read(['location_id'])[0]
                if parent_location_dest_id and parent_location_dest_id['location_id'] and parent_location_dest_id['location_id'][0]:

                    plocation_dest_id = self.env['stock.location'].browse(parent_location_dest_id['location_id'][0])
                    pick['location_dest_id']['location_id'] = plocation_dest_id.read(['id', 'display_name', 'loc_format', 'location_id'])[0]

                    if plocation_dest_id and plocation_id.location_id:
                        gplocation_dest_id = plocation_id.location_id
                        pick['location_dest_id']['location_id']['location_id'] = gplocation_dest_id.read(['display_name'])[0]
        return res