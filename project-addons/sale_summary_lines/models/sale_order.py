# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from odoo.addons import decimal_precision as dp


class SaleSummaryLine(models.Model):
    _name = 'sale.summary.line'
    _description = 'Sales Summary Line'
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    invoice_lines = fields.Many2many('account.invoice.line', 'sale_summary_line_invoice_rel', 'order_summary_line_id', 'invoice_line_id', string='Invoice Lines', copy=False)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

    price_reduce = fields.Float(compute='_get_price_reduce', string='Price Reduce', digits=dp.get_precision('Product Price'), readonly=True, store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_reduce_taxinc = fields.Monetary(compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True, store=True)
    price_reduce_taxexcl = fields.Monetary(compute='_get_price_reduce_notax', string='Price Reduce Tax excl', readonly=True, store=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)
    order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', readonly=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')
    qty_invoiced = fields.Float(
        compute='_get_summary_invoice_qty', string='Invoiced Quantity', store=True, readonly=True,
        compute_sudo=True,
        digits=dp.get_precision('Product Unit of Measure'))
    qty_to_invoice = fields.Float(
        compute='_get_summary_to_invoice_qty', string='To Invoice Quantity', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    qty_delivered = fields.Float('Delivered Quantity')


    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_summary_invoice_qty(self):
        
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'out_invoice':
                        qty_invoiced += invoice_line.quantity
                    elif invoice_line.invoice_id.type == 'out_refund':
                        qty_invoiced -= invoice_line.quantity
            line.qty_invoiced = qty_invoiced

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_summary_to_invoice_qty(self):
        
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.onchange('product_uom_qty')
    def product_uom_change(self):
        
        self.qty_delivered = self.product_uom_qty


    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0


    @api.depends('state', 'product_uom_qty', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
       
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        
        journal = self.env['account.journal'].search([], limit=1)[0]
        account = journal.default_debit_account_id

        
        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
        }
        return res

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative (refund).

            .. deprecated:: 12.0
                Replaced by :func:`invoice_line_create_vals` which can be used for creating
                `account.invoice.line` records in batch

            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns recordset of account.invoice.line created
        """
        return self.env['account.invoice.line'].create(
            self.invoice_line_create_vals(invoice_id, qty))

    def invoice_line_create_vals(self, invoice_id, qty):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative
            (refund).

            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns list of dict containing creation values for account.invoice.line records
        """
        vals_list = []
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision) or not line.product_id:
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'summary_line_ids': [(6, 0, [line.id])]})
                vals_list.append(vals)
        return vals_list



class SaleOrder(models.Model):
    _inherit = "sale.order"

    use_summary_lines = fields.Boolean('Use Summary Lines', default=False)
    summary_line_ids = fields.One2many('sale.summary.line', 'order_id', 
                                        string='Summary Lines', 
                                        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, 
                                        copy=True, 
                                        auto_join=True)

    summary_amount_untaxed = fields.Monetary(string='Summary Untaxed Amount', store=True, readonly=True, compute='_summary_amount_all')
    summary_amount_tax = fields.Monetary(string='Summary Taxes', store=True, readonly=True, compute='_summary_amount_all')
    summary_amount_total = fields.Monetary(string='Summary Total', store=True, readonly=True, compute='_summary_amount_all')


    @api.depends('summary_line_ids.price_total')
    def _summary_amount_all(self):
        """
        Compute the total summary amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.summary_line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'summary_amount_untaxed': amount_untaxed,
                'summary_amount_tax': amount_tax,
                'summary_amount_total': amount_untaxed + amount_tax,
            })

    @api.constrains('summary_amount_total', 'amount_total')
    def _check_summary_amount(self):
        precision = self.env['decimal.precision'].precision_get('Product Price')

        if self.use_summary_lines and float_compare(self.summary_amount_total, self.amount_total, precision_digits=precision) != 0:
            raise ValidationError(_('El importe total de las lineas resumen no coincide con el importe del pedido'))

    @api.model_cr
    def _register_hook(self):

        def new_action_invoice_create(self, grouped=False, final=False):
            """
            Create the invoice associated to the SO.
            :param grouped: if True, invoices are grouped by SO id. If False,
            invoices are grouped by (partner_invoice_id, currency)
            :param final: if True, refunds will be generated if necessary
            :returns: list of created invoices
            """
            inv_obj = self.env['account.invoice']
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            invoices = {}
            references = {}
            invoices_origin = {}
            invoices_name = {}

            # Keep track of the sequences of the lines
            # To keep lines under their section
            inv_line_sequence = 0
            for order in self:
                group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

                # We only want to create sections that have at least one invoiceable line
                pending_section = None

                # Create lines in batch to avoid performance problems
                line_vals_list = []
                # sequence is the natural order of order_lines

                # START HOOK
                if not order.use_summary_lines:
                # END HOOK
                    for line in order.order_line:
                        if line.display_type == 'line_section':
                            pending_section = line
                            continue
                        if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                            continue
                        if group_key not in invoices:
                            inv_data = order._prepare_invoice()
                            invoice = inv_obj.create(inv_data)
                            references[invoice] = order
                            invoices[group_key] = invoice
                            invoices_origin[group_key] = [invoice.origin]
                            invoices_name[group_key] = [invoice.name]
                        elif group_key in invoices:
                            if order.name not in invoices_origin[group_key]:
                                invoices_origin[group_key].append(order.name)
                            if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                                invoices_name[group_key].append(order.client_order_ref)

                        if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                            if pending_section:
                                section_invoice = pending_section.invoice_line_create_vals(
                                    invoices[group_key].id,
                                    pending_section.qty_to_invoice
                                )
                                inv_line_sequence += 1
                                section_invoice[0]['sequence'] = inv_line_sequence
                                line_vals_list.extend(section_invoice)
                                pending_section = None

                            inv_line_sequence += 1
                            inv_line = line.invoice_line_create_vals(
                                invoices[group_key].id, line.qty_to_invoice
                            )
                            inv_line[0]['sequence'] = inv_line_sequence
                            line_vals_list.extend(inv_line)
                # START HOOK
                else:
                    for line in order.summary_line_ids:
                        if  float_is_zero(line.qty_to_invoice, precision_digits=precision):
                            continue
                        if group_key not in invoices:
                            inv_data = order._prepare_invoice()
                            invoice = inv_obj.create(inv_data)
                            references[invoice] = order
                            invoices[group_key] = invoice
                            invoices_origin[group_key] = [invoice.origin]
                            invoices_name[group_key] = [invoice.name]
                        elif group_key in invoices:
                            if order.name not in invoices_origin[group_key]:
                                invoices_origin[group_key].append(order.name)
                            if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                                invoices_name[group_key].append(order.client_order_ref)

                        if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):

                            inv_line_sequence += 1
                            inv_line = line.invoice_line_create_vals(
                                invoices[group_key].id, line.qty_to_invoice
                            )
                            inv_line[0]['sequence'] = inv_line_sequence
                            line_vals_list.extend(inv_line)
                # END HOOK

                if references.get(invoices.get(group_key)):
                    if order not in references[invoices[group_key]]:
                        references[invoices[group_key]] |= order

                self.env['account.invoice.line'].create(line_vals_list)

            for group_key in invoices:
                invoices[group_key].write({'name': ', '.join(invoices_name[group_key])[:2000],
                                        'origin': ', '.join(invoices_origin[group_key])})
                sale_orders = references[invoices[group_key]]
                if len(sale_orders) == 1:
                    invoices[group_key].reference = sale_orders.reference

            if not invoices:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            self._finalize_invoices(invoices, references)
            return [inv.id for inv in invoices.values()]


        self._patch_method('action_invoice_create', new_action_invoice_create)

        return super(SaleOrder, self)._register_hook()


    @api.depends('state', 'order_line.invoice_status', 'order_line.invoice_lines',
                    'summary_line_ids.invoice_status', 'summary_line_ids.invoice_lines')
    def _get_invoiced(self):
        res = super()._get_invoiced()
        for order in self.filtered(lambda o: o.use_summary_lines):
            if order.use_summary_lines:
                #line_invoice_status_all = [(d['order_id'][0], d['invoice_status']) for d in self.env['sale.order.line'].read_group([('order_id', 'in', self.ids), ('product_id', '!=', deposit_product_id.id)], ['order_id', 'invoice_status'], ['order_id', 'invoice_status'], lazy=False)]
                line_invoice_status_all = [(d['order_id'][0], d['invoice_status']) for d in self.env['sale.summary.line'].read_group([('order_id', 'in', self.ids)], ['order_id', 'invoice_status'], ['order_id', 'invoice_status'], lazy=False)]
                invoice_ids = order.summary_line_ids.mapped('invoice_lines').mapped('invoice_id').filtered(lambda r: r.type in ['out_invoice', 'out_refund'])
                line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]

                if order.state not in ('sale', 'done'):
                    invoice_status = 'no'
                elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                    invoice_status = 'to invoice'
                elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                    invoice_status = 'invoiced'
                
                else:
                    invoice_status = 'no'

                order.update({
                    'invoice_count': len(set(invoice_ids.ids)),
                    'invoice_ids': invoice_ids.ids,
                    'invoice_status': invoice_status
                })

                
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"            

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced',
                'order_id.use_summary_lines', 'order_id.summary_line_ids')
    def _compute_invoice_status(self):
        lines_not_summary  = self.mapped('order_id').filtered(lambda o: not o.use_summary_lines).order_line
        lines_summary  = self.mapped('order_id').filtered(lambda o: o.use_summary_lines).order_line
        super(SaleOrderLine, lines_not_summary)._compute_invoice_status()
        for line in lines_summary:
            if all(l.invoice_status == 'invoiced' for l in line.order_id.summary_line_ids):
                line.invoice_status ='invoiced'
            elif any(l.invoice_status == 'to invoice' for l in line.order_id.summary_line_ids):
                line.invoice_status ='to invoice'
            else:
                line.invoice_status ='no'

            

