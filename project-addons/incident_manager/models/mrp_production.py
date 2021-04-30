# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = ["mrp.production", "model.incident.base"]
    _name = "mrp.production"