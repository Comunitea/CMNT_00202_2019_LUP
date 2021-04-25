# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = ["crm.lead", "model.incident.base"]
    _name = "crm.lead"

