# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class StockPicking(models.Model):

    _inherit = "stock.picking"

    label_printed = fields.Boolean('Label printed')
    commercial_partner_id = fields.Many2one(related='partner_id.commercial_partner_id')
    valued = fields.Boolean(
        related='commercial_partner_id.valued_picking', readonly=True
    )


    @api.multi
    def _compute_valued(self):
        for pick in self:
            pick.valued = pick.partner_id.commercial_partner_id.valued_picking


    def print_label(self):
        self.write({'label_printed': True})
        return self.env.ref('custom_documents_lupeon.report_move_label').\
            report_action(self)
