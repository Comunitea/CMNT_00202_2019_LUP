# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class DeliverCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('gls', 'GLS'),('correos_express', 'Correos Express'), ('dhl', 'DHL')])
    
    
    
    def gls_get_tracking_link(self, picking):
        return (
            'https://m.gls-spain.es/e/%s' % (
                picking.carrier_tracking_ref
            )
        )
        
    def correos_express_get_tracking_link(self, picking):
        return (
            'https://s.correosexpress.com/SeguimientoSinCP/search?n=%s' % (
                picking.carrier_tracking_ref
            )
        )
        
    def dhl_get_tracking_link(self, picking):
        return (
            'https://www.dhl.com/en/express/tracking.html?AWB=%s&brand=DHL' % (
                picking.carrier_tracking_ref
            )
        )