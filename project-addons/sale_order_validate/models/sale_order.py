# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        """
        Check if order partner supping is complete.
        """
        for order in self:
            msg = order._check_country_restrictions()
            if msg:
                raise ValidationError(msg)
            msg = order._check_transport_restrictions()
            if msg:
                raise ValidationError(msg)
        for order in self:
            if not order.prestashop_state:
                if (not order.partner_shipping_id.country_id or 
                    (not order.partner_shipping_id.state_id and order.partner_shipping_id.country_id.state_ids) or 
                    not (order.partner_shipping_id.mobile or order.partner_shipping_id.phone) or
                    not order.partner_shipping_id.zip):
                    raise UserError(_('No están informados todos los campos necesarios de la dirección de entrega. Por favor revise: País, provincia, código postal y teléfono'))
        
        res = super().action_confirm()
        return res    


    def get_delivery_price(self):
        for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
            carrier_id = self.carrier_id
            so_lines = order.order_line.filtered(lambda x: x.product_id.transport_restrictions)
            if so_lines and self.carrier_id.allow_transport_restrictions:
                msg = 'Los siguintes artículos no tiene restricciones de transporte'
                for line in so_lines:
                    msg = '{}\n{}'.format(msg, line.product_id.display_name)
                raise ValidationError (msg)
    

    def _check_country_restrictions(self):
        msg = False
        ## HArdcode  x.company_id.id == 2 para dativic
        if self.company_id.cost_sheet_sale:
            forbidden_products_ids = self.env['product.product']
            country_id = self.partner_shipping_id.country_id
            for line in self.order_line.filtered(lambda x:  x.product_id.forbidden_country_ids):
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

    @api.onchange('partner_shipping_id')
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
            for line in self.order_line.filtered(lambda x: x.product_id.transport_restrictions):
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



    @api.multi
    def print_quotation(self):
        if not self.env.context.get('bypass_checks', False):
            for order in self:
                res = order.check_quotation_conditions()
                if res['alert']:
                    return self.env['check.send.print.wiz'].create({
                            'exception_msg': res['message'],
                            'order_id': order.id,
                            'continue_method': 'print_quotation',
                        }).action_show()

        return super().print_quotation()


    @api.multi
    def action_quotation_send(self):
        if not self.env.context.get('bypass_checks', False):
            for order in self:
                res = order.check_quotation_conditions()
                if res['alert']:
                    return self.env['check.send.print.wiz'].create({
                            'exception_msg': res['message'],
                            'order_id': order.id,
                            'continue_method': 'action_quotation_send',
                        }).action_show()

        return super().action_quotation_send()

    @api.multi
    def check_quotation_conditions(self):
        res = {'message': '',
                'alert': False,
                'continue':True
        }
        for order in self:
            if order.company_id.cost_sheet_sale:
                # CHECK DIAMETER
                diameter_values = order.order_line.mapped('product_id').\
                    mapped('attribute_value_ids').\
                    filtered(lambda v: 'Diámetro' in v.attribute_id.name).\
                    mapped('name')
                diameter_values = list(set(diameter_values))
                if len(diameter_values) > 1:
                    res['message'] += "El pedido incluye productos de diferentes diámetros. Revisar antes de continuar.\n"
                    res['alert'] = True

                # CHECK DELIVERY
                delivery_line = order.order_line.mapped('product_id').filtered(lambda p: p.default_code=='SHIP')
                if not delivery_line:
                    res['message'] += "No se han incluido gastos de envío en el pedido. Revisar antes de continuar.\n"
                    res['alert'] = True
                # CHECK RESERVES
                if not order.with_reserves:
                    res['message'] += "No se ha realizado ninguna reserva de stock. Revisar antes de continuar.\n"
                    res['alert'] = True

            # CHECK SUBCONTACT
            if (not order.partner_shipping_id.id in order.partner_id.child_ids.ids and order.partner_shipping_id.id != order.partner_id.id) or \
               (not order.partner_invoice_id.id in order.partner_id.child_ids.ids and order.partner_invoice_id.id != order.partner_id.id) :
                res['message'] += "La dirección de entrega/factura no es un subcontacto del cliente. Revisar antes de continuar.\n"
                res['alert'] = True
            # CHECK COUNTRY
            if order.partner_id.country_id.id != order.partner_invoice_id.country_id.id:
                res['message'] += "El país de facturación es distinto al de entrega. Consultar con ADMINISTRACIÓN antes de continuar.\n"
                res['alert'] = True
            if order.fiscal_position_id.vat_required and not order.partner_id.commercial_partner_id.vat:
                res['message'] += "El cliente no tiene NIF asignado. Consultar con ADMINISTRACIÓN antes de continuar.\n"
                res['alert'] = True

            
            return res
                


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def check_restrictions(self):
        country_id = self.order_id.partner_shipping_id.country_id
        if country_id and country_id in self.product_id.forbidden_country_ids:
            raise ValidationError('El artículo {} no está permitido en {}'.format(self.product_id.display_name, country_id.name))

        carrier_id = self.order_id.carrier_id
        if self.product_id.transport_restrictions and carrier_id and not carrier_id.allow_transport_restrictions:
            raise ValidationError('El artículo {} tiene restricciones para el transportista en {}'.format(self.product_id.display_name, carrier_id.display_name))