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
