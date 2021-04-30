# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        """
        Check if order partner supping is complete.
        """
        for picking in self:
            if picking.picking_type_id.code =='outgoing':
                msg = picking._check_country_restrictions()
                if msg:
                    raise ValidationError(msg)
                msg = picking._check_transport_restrictions()
                if msg:
                    raise ValidationError(msg)
    
        
        res = super().button_validate()
        return res    
    

    def _check_country_restrictions(self):
        msg = False
        if self.company_id.cost_sheet_sale:
            forbidden_products_ids = self.env['product.product']
            country_id = self.partner_id.country_id
            for line in self.move_lines.filtered(lambda x:  x.product_id.forbidden_country_ids):
                if country_id in line.product_id.forbidden_country_ids:
                    forbidden_products_ids |= line.product_id

            if forbidden_products_ids:
                msg = 'Los siguientes produtos tienen restricciones para el envío a {}:'.format(country_id.name)
                for p_id in forbidden_products_ids:
                    msg = '{}\n{}'.format(msg, p_id.display_name)
        return msg
    
    def return_checks(self, msg):
        if msg:
            if self.state in ['sale', 'done']:
                raise ValidationError(msg)
                
            else:
                return {'warning': {
                            'title': 'Aviso!',
                            'message': msg}
                }

    @api.onchange('partner_id')
    def check_country_restrictions(self):
        self.ensure_one()
        msg = self._check_country_restrictions()
        return self.return_checks(msg)

    def _check_transport_restrictions(self):
        msg = False
        ## HArdcode  x.company_id.id == 2 para dativic
        if self.company_id.cost_sheet_sale:
            forbidden_products_ids = self.env['product.product']
            carrier_id = self.carrier_id
            if not carrier_id or carrier_id.allow_transport_restrictions:
                return False
            for line in self.move_lines.filtered(lambda x: x.product_id.transport_restrictions):
                forbidden_products_ids |= line.product_id
            if forbidden_products_ids:
                msg = 'Los siguientes produtos tienen restricciones para el envío para el proveedor {}:'.format(carrier_id.display_name)
                for p_id in forbidden_products_ids:
                    msg = '{}\n{}'.format(msg, p_id.display_name)
        return msg
    
    @api.onchange('carrier_id')
    def check_transport_restrictions(self):
        self.ensure_one()
        msg = self._check_transport_restrictions()
        return self.return_checks(msg)


