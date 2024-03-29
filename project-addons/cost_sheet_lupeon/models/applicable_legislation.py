# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

class ApplicableLegislation(models.Model):

    _name = 'applicable.legislation'
    _description = "Legislación aplicable"

    name = fields.Char('Sector')
    norma = fields.Char('Norma')