# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
# from odoo.exceptions import UserError, ValidationError

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    allow_transport_restrictions = fields.Boolean("Permitir productos con restricciones de transporte", default=False)
