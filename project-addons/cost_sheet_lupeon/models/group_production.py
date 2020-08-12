# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GroupProduction(models.Model):

    _name = "group.production"

    name = fields.Char('Name')
    production_ids = fields.One2many(
        'mrp.production', 'group_mrp_id', 'Gropued Productions')
    
    material_ids = fields.One2many(
        'group.material.line', 'group_mrp_id', 'Materials to consume')
    repart_material_ids = fields.One2many(
        'repart.material.line', 'group_mrp_id', 'Production material')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange')
    
    total_time = fields.Float('Total time')
    
    def action_confirm_group(self):
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
        self.state = 'confirmed'
    
    def action_plan_group(self):
        self.ensure_one()
        if not self.total_time:
            raise UserError('You need to set the time for this production')
        
        if any(not ml.real_qty for ml in self.material_ids):
            raise UserError('You need to set up the real consumes of material')
        
        for ml in self.material_ids:
            total_qty = sum(
                [x.qty for x in self.repart_material_ids if 
                 x.product_id == ml.product_id])
            # Reparto proporcional consumos
            for rml in self.repart_material_ids.filtered(
                    lambda x: x.product_id == ml.product_id):
                percent = rml.qty / total_qty
                rml.real_qty = ml.real_qty * percent
        self.state = 'planned'
                

    def action_done_group(self):
        self.ensure_one()
        for rml in self.repart_material_ids:
            mrp = rml.production_id
            for wo in mrp.workorder_ids:
                if wo.state == 'done':
                    continue
                wo.button_start()
                wo.duration = self.total_time  # TODO repartir
                wo.record_production()
            
            mrp.action_assign()
            if mrp.availability != 'assigned':
                raise UserError(
            _('Cant reserve materials form production %s') % mrp.name)
            mrp.button_mark_done()
        self.state = 'done'

    def action_cancel_group(self):
        self.ensure_one()
        self.material_ids.unlink()
        self.repart_material_ids.unlink()
        self.state = 'cancel'

    def action_draft_group(self):
        self.ensure_one()
        self.state = 'draft'


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