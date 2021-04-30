# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

class PartFeatures(models.Model):

    _name = 'part.feature'
    _description = "Sector"

    name = fields.Char('Sector')
