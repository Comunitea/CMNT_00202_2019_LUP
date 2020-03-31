# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

class Material(models.Model):

    _name = 'material'

    name = fields.Char('Name')
    gr_cc = fields.Float('Gr/cc')
    euro_kg = fields.Float('€/kg')
    factor_hour = fields.Float('Factor hour')