# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class GroupProduction(models.Model):

    _name = "group.production"

    name = fields.Char('Name')
    production_ids = fields.One2many(
        'mrp.production', 'group_mrp_id', 'Gropued Productions')
    
    material_ids = fields.One2many(
        'group.material.line', 'group_mrp_id', 'Materials to consume')
    repart_material_ids = fields.One2many(
        'repart.material.line', 'group_mrp_id', 'Production material')
    state = fields.Selection([('confirmed', 'Confirmed')], 'State')
    
    def setup_group(self):
        self.ensure_one()
        product_qtys = {}
        for mrp in self.production_ids:
            for move in mrp.move_raw_ids:
                if move.product_id not in product_qtys:
                    product_qtys[move.product_id] = 0.0
                product_qtys[move.product_id] += move.product_uom_qty

                vals = {
                    'group_mrp_id': self.id,
                    'product_id': move.product_id.id,
                    'qty': move.product_uom_qty,
                    'production_id': mrp.id
                }
                self.env['repart.material.line'].create(vals)
        
        for product in product_qtys:
            vals = {
                'group_mrp_id': self.id,
                'product_id': product.id,
                'qty': product_qtys[product]
            }
            self.env['group.material.line'].create(vals)




class GroupMaterialLine(models.Model):

    _name = "group.material.line"

    group_mrp_id = fields.Many2one('group.production', 'Group', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty = fields.Float('To consume', readonly=True)
    real_qty = fields.Float('Consumed quantity')


class RepartMaterialLine(models.Model):

    _name = "repart.material.line"

    group_mrp_id = fields.Many2one('group.production', 'Group', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    production_id = fields.Many2one('mrp.production', 'Production', readonly=True)
    qty = fields.Float('To consume', readonly=True)
    real_qty = fields.Float('Consumed quantity')