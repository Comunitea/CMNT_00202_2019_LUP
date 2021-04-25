# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api,_
from openerp.exceptions import ValidationError

class ProductPurchaseLineWizard(models.TransientModel):
    _name = "product.purchase.line.wizard"
    _description = "Asistente lineas de compra"
    
    
    product_id = fields.Many2one('product.product')
    product_qty = fields.Float("Quantity", default=0.00)
    product_purchase_wzd_id = fields.Many2one('product.purchase.wizard')
    twelve_months_ago = fields.Float('12', readonly=True)
    six_months_ago = fields.Float('6', readonly=True) 
    last_month_ago = fields.Float('1', readonly=True) 
    virtual_available = fields.Float('Previsto', readonly=True)
    qty_available = fields.Float('A mano', readonly=True)
    reordering_min_qty = fields.Float('Max', readonly=True)
    reordering_max_qty = fields.Float('Min', readonly=True)
       
class ProductPurchaseWizard(models.TransientModel):

    _name = "product.purchase.wizard"
    _description = "Asistente de compras"

    @api.multi
    def _compute_purchased_qties(self):
        
        self.purchased_qties = sum(x.product_qty for x in self.line_ids)
        


    supplier_id = fields.Many2one('res.partner', 'Supplier')
    purchase_order = fields.Many2one('purchase.order')
    line_ids = fields.One2many('product.purchase.line.wizard', 'product_purchase_wzd_id')
    purchased_qties = fields.Float('Totat Ordered Qty', compute=_compute_purchased_qties)
    
    def add_to_purchase_order(self):

        if not self.purchase_order:
            raise ValidationError(_("No order selected"))
        OrderLine = self.env['purchase.order.line']
        ids = [x.product_id.id for x in self.line_ids]
        domain = [('order_id', '=', self.purchase_order.id), ('product_id','in', ids)]
        lines_to_unlink = self.env['purchase.order.line'].search(domain)
        lines_to_unlink.unlink()

        for line in self.line_ids:
            order_line = OrderLine.new({
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id,
                'order_id': self.purchase_order.id,
                'product_qty': line.product_qty,
                'partner_id': self.purchase_order.partner_id.id})
            order_line.onchange_product_id()
            order_line.product_qty = line.product_qty
            order_line_vals = order_line._convert_to_write(
                order_line._cache)
            self.purchase_order.order_line.create(order_line_vals)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'res_id': self.purchase_order.id,
            'context': self.env.context
        }


    @api.model
    def default_get(self, fields):
        product_ids = self.env.context.get('active_ids', [])
   
        res = super(ProductPurchaseWizard, self).default_get(fields)
        products = self.env['product.product'].browse(product_ids)
        
        lines =  []
        if not product_ids:
            return res
        lines = [
            (
                0,
                0,
                {
                    'product_id': product.id,
                    'product_qty': product.purchase_qty,
                    'twelve_months_ago': product.twelve_months_ago,
                    'six_months_ago': product.six_months_ago,
                    'last_month_ago': product.last_month_ago,
                    'virtual_available': product.virtual_available,
                    'qty_available': product.qty_available,
                    'reordering_min_qty': product.reordering_min_qty,
                    'reordering_max_qty': product.reordering_max_qty
                },
            )
            for product in products
        ]
        res['purchased_qties'] = sum(x.purchase_qty for x in products)
        if len(products.mapped('main_supplier_id')) == 1:
            res['supplier_id'] = products.mapped('main_supplier_id').id
            po = self.env['purchase.order'].search(
                [('partner_id', 'child_of', products.mapped('main_supplier_id').id),
                 ('state','not in',['purchase','cancel','done'])])
            if len(po) == 1:
                res['purchase_order'] = po.id
            
        res['line_ids'] =lines
        return res

  
    def refresh(self):
        _action = self.env.ref("purchase_custom_lupeon.action_add_product_purchase_line_wzd")
        action = _action.read()[0]        
        action["res_id"] = self.id
        return action


