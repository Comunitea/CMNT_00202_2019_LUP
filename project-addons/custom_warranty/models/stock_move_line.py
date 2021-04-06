# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _action_done(self):
        res = super()._action_done()
        ## El action done de odoo tiene un bug y devuelve un self con un elemento borrado 
        # si se procesa mas cantidad que la que se reserva por lo que falla aquí
        warranty_moves = self.filtered(lambda x: x.exists() and x.lot_id and x.product_id.with_warranty)
        if warranty_moves:
            for move_line in warranty_moves.filtered(lambda r: r.picking_id.picking_type_id.code == "outgoing"):
                ## Es un movimiento de salida
                serial_id = move_line.lot_id
                product_id = move_line.product_id
                if serial_id.sale_date:
                    raise UserError (_('Serial {} is under warranty. Please, reset warranties before compute new warranties'.format(serial_id.name)))
                life_date = move_line.date + relativedelta(
                            days=product_id.life_time
                        )
                vals = {'sale_date': move_line.date.date(),
                        'under_warranty': True,
                        'with_warranty': True,
                        'warranty_partner_id': move_line.picking_id.partner_id.id, 
                        'life_date': life_date.date()}
                serial_id.write(vals)
        
            ## Reseteo el número de serie y la garantía si la ubicación de origen es clientes y la de destino es interna. Si no habría que hacerlo manualmente.
            for move_line in self.filtered(lambda r: 
                            r.location_id.usage == 'customer' and 
                            r.location_dest_id.usage == 'internal'):
                serial_id = move_line.lot_id
                product_id = move_line.product_id
                msg ="Serial number returned ad {}.Reset warranty: <ul><li>Partner: {}</li><li>Sale date: {} </li><li>End Warranty: {} </li>".format(move_line.date, serial_id.warranty_partner_id.display_name, serial_id.sale_date, serial_id.life_date)
                serial_id.message_post(body=msg)
                
                vals = {'sale_date': False,
                        'under_warranty': False,
                        'with_warranty': True,
                        'warranty_partner_id': False, 
                        'life_date': False}
                serial_id.write(vals)


        return res
