# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    eic = fields.Boolean('Pedido con facturación electrónica',default=False)