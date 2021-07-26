# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit ="product.template"

    #is_delivery = fields.Boolean(string="Is a Delivery", default=False)
    invoice_with_products = fields.Boolean(string="Facturar solo con envíos", default=False)