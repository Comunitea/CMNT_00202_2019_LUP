# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class StockPicking(models.Model):

    _inherit = "stock.picking"

    label_printed = fields.Boolean('Label printed')

    def print_label(self):
        self.write({'label_printed': True})
        return self.env.ref('custom_documents_lupeon.report_move_label').\
            report_action(self)
