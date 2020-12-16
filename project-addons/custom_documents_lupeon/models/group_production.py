# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class GroupProduction(models.Model):

    _inherit = "group.production"

    @api.multi
    def print_labels(self):
        productions = self.register_ids.mapped('workorder_id.production_id')
        res = self.env.ref('custom_documents_lupeon.report_production_label')\
            .report_action(productions)
        return res
