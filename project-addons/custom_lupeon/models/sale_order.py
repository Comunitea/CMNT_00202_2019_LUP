# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.exceptions import UserError



class SaleOrder(models.Model):

    _inherit = "sale.order"

    ship_cost = fields.Monetary(string='Ship Cost', default=0.0)
    num_line = fields.Char(string='Nº Line')

    @api.multi
    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.num_line:
            vals['num_line'] = self.num_line
        return vals

    @api.multi
    def action_confirm(self):
        """
        Check if order requires client_order_ref.
        Creation of product sheet ids
        """
        for order in self:
            if (order.partner_id.require_num_order):
                order.client_order_ref = 'PENDIENTE'
        res = super().action_confirm()
        return res
    
    @api.multi
    def write(self, vals):
        """
        Propagar cambio de referencia a la factura
        """
        res = super().write(vals)
        if vals.get('client_order_ref'):
            invoices = self.mapped('invoice_ids')
            if invoices:
                invoices.write({'name': vals['client_order_ref']})
        return res
    
    @api.multi
    def create_procurements_all(self):   
        for order in self:
            order.order_line.create_procurements()
            
    @api.multi
    def action_barcode_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        pickings = self.mapped('picking_ids').filtered(lambda x: x.state == 'assigned')
        if pickings:
            if len(pickings) == 1:
                return pickings[0].open_picking_client_action()
            else:
                pt = pickings.mapped('picking_type_id')
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
                    res['domain'] = [('id', 'in', pickings.ids)]

                return res
        raise UserError(_('No pickings in assigned state to open'))
        return


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    reserved = fields.Boolean('Reserved', compute="_is_reserve")

    @api.multi
    def _is_reserve(self):
        for line in self:
            if line.move_ids.filtered(lambda x: x.state == 'assigned'):
                line.reserved = True

    @api.multi
    def _action_launch_stock_rule_anticiped(self):
        """
        Copia del método pero sin que se salte la logica por no estart en
        estado sale
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def create_procurements(self):
        for line in self:
            # Se necesita la fecha de confirmación para que no falle
            line.order_id.confirmation_date = fields.Datetime.now()
            line._action_launch_stock_rule_anticiped()
            line.move_ids.filtered(lambda x: x.state == 'confirmed')._action_assign()
           
        return {'type': 'ir.actions.client', 'tag': 'reload'}