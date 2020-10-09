# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class ResCompany(models.Model):

    _inherit = "res.company"

    ing_hours = fields.Integer('Horas ingenieria', default=55)
    tech_hours = fields.Integer('Horas técnico', default=35)
    help_hours = fields.Integer('Horas ayudante', default=35)
    km_cost = fields.Float('Coste Km', default=0.30)
