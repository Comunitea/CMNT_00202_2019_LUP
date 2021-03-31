# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields, _
from odoo.exceptions import UserError

class UtmCampaign(models.Model):
    _inherit = "utm.campaign"

    company_id = fields.Many2one('res.company', 
                                string='Company', 
                                required=False,
                                default=lambda self: self.env.user.company_id)
