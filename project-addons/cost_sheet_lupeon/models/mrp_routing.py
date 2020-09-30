# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class MrpRouting(models.Model):

    _inherit = 'mrp.routing'

    created_on_fly = fields.Boolean('Creado al vuelo')