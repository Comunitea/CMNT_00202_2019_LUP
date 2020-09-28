# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class MrpWorkorder(models.Model):

    _inherit = "mrp.workorder"

    sheet_id = fields.Many2one(
        'cost.sheet', 'Cost Sheet', related='production_id.sheet_id')

    # No quiero que cree checks de calidad
    def _create_checks(self):
        return