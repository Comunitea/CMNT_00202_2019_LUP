# -*- coding: utf-8 -*-
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api,_
from openerp.exceptions import ValidationError

class ProductProductionLineWizard(models.TransientModel):
    _name = "product.production.line.wizard"
    _description = "Asistente lineas de producción"
    
    
    product_id = fields.Many2one('product.product',readonly=True)
    product_qty = fields.Float("Quantity", default=0.00)
    product_production_wzd_id = fields.Many2one('product.production.wizard')
    twelve_months_ago = fields.Float('12', readonly=True)
    six_months_ago = fields.Float('6', readonly=True ) 
    last_month_ago = fields.Float('1', readonly=True) 
    virtual_available = fields.Float('Previsto', readonly=True, force_save=True)
    qty_available = fields.Float('A mano', readonly=True, force_save=True)
    production_id = fields.Many2one('mrp.production', 'Actual Production', readonly=True, force_save=True)
    production_qty = fields.Float('Total en producciones')
       
class ProductProductionWizard(models.TransientModel):

    _name = "product.production.wizard"
    _description = "Asistente de producción"


    line_ids = fields.One2many('product.production.line.wizard', 'product_production_wzd_id')

    
    def create_production_order(self):

    
        Production = self.env['mrp.production']
        result_ids = []
        for line in self.line_ids:
            if line.production_id:
                # Actualiza cantidad por difenrecia total con a producir
                diff_prod = line.product_qty - line.production_qty
                if diff_prod < 0:
                    raise ValidationError(
                        _("La cantidad introducida para el producto %s es igual o inferior a la ya planificada para producir.")
                        % line.product_id.name
                    )
                    return False
                    
                if diff_prod >0:
                    update_wiz = self.env['change.production.qty'].create({
                        'mo_id': line.production_id.id,
                        'product_qty': line.production_id.product_qty + diff_prod
                    })
                    update_wiz.change_prod_qty()
                    result_ids.append(line.production_id.id)
            else:
                if line.product_id.variant_bom_ids:
                    new_prod =  Production.create({
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'bom_id': line.product_id.variant_bom_ids[0].id,
                        'product_qty': line.product_qty
                    })
                    new_prod.onchange_product_id()
                    new_prod.product_qty = line.product_qty
                    new_prod.action_assign()
                    result_ids.append(new_prod.id)

        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'view_id': False,
            'domain': [('id', 'in', result_ids)],
            'type': 'ir.actions.act_window',
            'context': self.env.context
        }


    @api.model
    def default_get(self, fields):
        product_ids = self.env.context.get('active_ids', [])
   
        res = super(ProductProductionWizard, self).default_get(fields)
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
                    'production_id': product.actual_production_id.id,
                    'production_qty': product.total_production_qty,
                },
            )
            for product in products
        ]
            
        res['line_ids'] =lines
        return res

  
    def refresh(self):
        _action = self.env.ref("production_needs.action_product_production_custom_all")
        action = _action.read()[0]        
        action["res_id"] = self.id
        return action


