# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

class Tinted(models.Model):

    _name = 'tinted'
    _description = "Tintado"

    name = fields.Char('Name')