# © 2021 Comunitea 
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, _


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.onchange("property_account_position_id")
    def on_change_ap(self):
        self.valued_picking = self.property_account_position_id.valued_picking
