# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta



class SaleOrder(models.Model):

    _inherit = "sale.order"

    ship_cost = fields.Monetary(string='Ship Cost', compute="_compute_ship_cost")
    ship_price = fields.Monetary(string='Ship Price', compute="_compute_ship_price")
    num_line = fields.Char(string='Nº Line')
    rejected = fields.Boolean('Rejected')
    rejected_reason = fields.Text('Rejected Reason')
    delivered = fields.Selection([('delivered', 'Delivered'),
                                    ('not_delivered', 'Not Delivered'),
                                    ('partially', 'Partially Delivered')],
                                string='Delivered',
                                default='not_delivered',
                                compute="_compute_delivered",
                                store=True)
    delivery_blocked = fields.Boolean("Entrega bloqueada", default=False)
    admin_fact = fields.Float("Factor admin.", compute="_compute_fa", 
                                readonly=True,
                                store = True)
    with_reserves = fields.Boolean("With Reserves", compute="_compute_reserves")


    # Se usa en una acción de servidor 
    def get_activity_deadline(self, activity_type_id):
      
        # Date.context_today is correct because date_deadline is a Date and is meant to be
        # expressed in user TZ
        base = fields.Date.context_today(self)
        
        return base + relativedelta(**{activity_type_id.delay_unit: activity_type_id.delay_count})

    
    def _compute_reserves(self):
        for order in self:
            order.with_reserves = any(line.reserved > 0 for line in order.order_line)

    @api.depends('partner_id')
    def _compute_fa(self):
        for order in self:
            order.admin_fact = order.partner_id._get_admin_fact()

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        if self.company_id.cost_sheet_sale:
            return self.env.ref('sale.action_report_pro_forma_invoice')\
                .with_context(discard_logo_check=True).report_action(self)
        else:
            return self.env.ref('custom_documents_lupeon.action_report_saleorder_lupeon')\
                .with_context(discard_logo_check=True).report_action(self)

    def _compute_ship_cost(self):
        for order in self:
            order.ship_cost = sum(order.picking_ids.mapped('ship_cost'))


    def _compute_ship_price(self):
        for order in self:
            
            ship_line =  order.order_line.filtered(lambda line: line.product_id.default_code=='SHIP')
            if ship_line:
                order.ship_price = ship_line[0].price_subtotal
            else:
                order.ship_price = 0
            

    @api.depends('picking_ids.delivered')
    def _compute_delivered(self):
        for order in self:
            delivery_pickings = order.picking_ids.filtered(lambda pick: pick.picking_type_id.code=='outgoing' and pick.state != 'cancel')
            if all(picking.delivered for picking in delivery_pickings):
                order.delivered = 'delivered'
            elif any(picking.delivered for picking in delivery_pickings):
                order.delivered = 'partially'
            else:
                order.delivered = 'not_delivered'
                

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
            if (order.partner_id.require_num_order and not
                    order.client_order_ref):
                order.client_order_ref = 'PENDIENTE'

            # Solo lupeon
            if (order.company_id.id == 1 and not order.commitment_date):
                raise UserError(_('You need to set commitment date.'))

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
    
    # @api.depends('margin', 'amount_untaxed', 'ship_cost', 'payment_mode_id')
    # def _compute_percent(self):
    #     for order in self:
    #         if order.margin and order.amount_untaxed:
    #             order.percent = ((order.margin - order.ship_cost - order.payment_mode_id.payment_cost) / order.amount_untaxed) * 100

    @api.depends('order_line.margin', 'ship_cost', 'payment_mode_id')
    def _product_margin(self):
        if self.env.in_onchange:
            for order in self:
                payment_cost = order.payment_mode_id and order.payment_mode_id.payment_cost or 0.0
                order.margin = sum(order.order_line.filtered(lambda r: r.state != 'cancel').mapped('margin')) - \
                    order.ship_cost - payment_cost
        else:
            # On batch records recomputation (e.g. at install), compute the margins
            # with a single read_group query for better performance.
            # This isn't done in an onchange environment because (part of) the data
            # may not be stored in database (new records or unsaved modifications).
            grouped_order_lines_data = self.env['sale.order.line'].read_group(
                [
                    ('order_id', 'in', self.ids),
                    ('state', '!=', 'cancel'),
                ], ['margin', 'order_id'], ['order_id'])
            for data in grouped_order_lines_data:
                order = self.browse(data['order_id'][0])
                payment_cost = order.payment_mode_id and order.payment_mode_id.payment_cost or 0.0
                order.margin = data['margin'] - \
                    order.ship_cost - payment_cost



class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    reserved = fields.Boolean('Reserved', compute="_is_reserve")
    qty_reserved = fields.Float('Qty Reserved', compute="_is_reserve")
    real_stock = fields.Float('Real stock', related="product_id.qty_available")


    @api.depends('product_id', 'product_uom_qty', 'qty_delivered', 'state')
    def _compute_qty_to_deliver(self):
        """ Based on _compute_qty_to_deliver method of sale.order.line
            model in Odoo v13 'sale_stock' module.
            This method is overwrited ofr Customer especification
        """
        for line in self:
            #line.qty_to_deliver = line.product_uom_qty - line.qty_delivered
            line.display_qty_widget = (line.product_type == 'product')

    @api.multi
    def _is_reserve(self):
        for line in self:
            if line.move_ids.filtered(lambda x: x.state in ('assigned', 'partially_available')):
                line.reserved = True
                line.qty_reserved = sum(move.reserved_availability for move in line.move_ids)

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
    
    @api.multi
    def _get_display_price(self, product):
        """
        Actualizar solo en compañía dativic
        """
        price = super()._get_display_price(product)
        if self.order_id.partner_id._get_admin_fact() and \
                self.order_id.company_id.id != 1:
            price_precision = self.env['decimal.precision'].precision_get(
            'Product Price')
            price = float_round(price * (1 + self.order_id.partner_id.\
                _get_admin_fact()/100), price_precision)
        return price
    
    @api.depends('product_id', 'customer_lead', 'product_uom_qty',
                 'order_id.warehouse_id', 'order_id.commitment_date')
    def _compute_qty_at_date(self):
        """
        Add reserved qty to compute calc
        """
        super()._compute_qty_at_date()
        for line in self:
            new_qty = line.virtual_available_at_date + line.qty_reserved
            line.virtual_available_at_date = new_qty
    
class SaleOrderState(models.Model):
    _inherit = "sale.order.state"

    trigger_delivered = fields.Boolean('Trigger Delivered')
    pending_payment = fields.Boolean('Pending Payment')
