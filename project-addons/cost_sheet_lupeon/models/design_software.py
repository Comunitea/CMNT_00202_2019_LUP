# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class DesignSoftware(models.Model):

    _name = 'design.software'
    _description = "Software de diseño"

    name = fields.Char('Name')
    price_hour = fields.Float('Price / hour')