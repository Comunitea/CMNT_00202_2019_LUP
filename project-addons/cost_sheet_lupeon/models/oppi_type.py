# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class OppiType(models.Model):

    _name = 'oppi.type'
    _description = "Tipo OPPI"

    name = fields.Char('Name')
    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Workcenter', required=True)