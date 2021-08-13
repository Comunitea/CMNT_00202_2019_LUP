# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
# from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    transport_restrictions = fields.Boolean("Restricciones de transporte", default=False)
    forbidden_country_ids = fields.Many2many('res.country', string="Paises no permitidos")
    forbidden_country_group_ids = fields.Many2many('res.country.group', string="Grupos de paises no permitidos")
    