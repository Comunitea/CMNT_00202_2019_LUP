# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class DeliverCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('gls', 'GLS'),('correos_express', 'Correos Express'), ('dhl', 'DHL')])
    ps_sync = fields.Boolean('Sincro PS', compute="_compute_ps", store=True)
    
    @api.depends('prestashop_bind_ids')
    def _compute_ps(self):
        for dc in self:
            if len(dc.prestashop_bind_ids) > 0:
                dc.ps_sync = True
            else:
                dc.ps_sync = False
    
    
    def gls_get_tracking_link(self, picking):
        return (
            'https://www.gls-spain.es/es/ayuda/seguimiento-envio/?match=%s' % (
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