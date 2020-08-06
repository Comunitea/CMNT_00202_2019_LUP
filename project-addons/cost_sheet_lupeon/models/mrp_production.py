# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

SHEET_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS P396'),
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('sls2', 'SLS'),
    ('dmls', 'DMLS'),
    ('unplanned', 'Imprevistos'),
    ('meets', 'Reuniones'),
    ('purchase', 'Compras'),
]

class MrpProduction(models.Model):

    _inherit = "mrp.production"

    sheet_id = fields.Many2one('cost.sheet', 'Cost Sheet', readonly=True)
    sheet_type = fields.Selection(SHEET_TYPES, string='Sheet type',
                                  related='sheet_id.sheet_type')
    sale_id = fields.Many2one('sale.order', 'Sale Order',
                              related='sheet_id.sale_id', readonly=True, 
                              store=True)
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line',
                                   related='sheet_id.sale_line_id', readonly=True, 
                                   store=True)
    
    line_ref = fields.Char('Referencia')
    line_name = fields.Char('Descripción')
    ok_tech = fields.Boolean('OK tech', copy=False, readonly=True)
    no_ok_tech = fields.Integer('Qty no ok tech', copy=False, readonly=True)
    ok_quality = fields.Boolean('OK quality', copy=False, readonly=True)
    no_ok_quality = fields.Integer('Qty no ok tech', copy=False, readonly=True)

    repeated_production_ids = fields.One2many('mrp.production', 'origin_production_id', 'Repeated production')
    origin_production_id = fields.Many2one('mrp.production', 'Origin production')


    def create_partial_mrp(self, qty, mode):
        self.ensure_one()

        version = len(self.repeated_production_ids) + 1
        mrp = self.copy({
            'name': self.name + ' - R%s' % version,
            'product_uom_qty': qty,
            'sheet_id': self.sheet_id,
            'origin_production_id': self.id,
        })

        vals = {
            'product_id': self.product_id.id,
            'product_uom_qty': qty,
            'product_uom_id': self.product_uom_id.id,
            'production_id': self.id,
            'origin': self.name + ' (%s)' % mode
        }
        scrap = self.env['stock.scrap'].create(vals)
        scrap.action_validate()
