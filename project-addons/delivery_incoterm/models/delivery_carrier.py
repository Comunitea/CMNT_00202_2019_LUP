# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields,_
from odoo.exceptions import UserError

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    incoterm = fields.Many2one(
        'account.incoterms', 'Incoterms',
        help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
