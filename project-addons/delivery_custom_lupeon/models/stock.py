# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_generate_carrier_label(self):
        if self.carrier_weight == 0 and self.weight != 0:
            self.carrier_weight = self.weight
        return super().action_generate_carrier_label()

    @api.multi
    def button_validate(self):
        for pick in self:
            # Module delivery_package_number puts negative values here
            # when there are no result_package_id in the lines.
            if pick.number_of_packages <= 0:
                pick.number_of_packages = 1
            if pick.carrier_packages <= 0:
                pick.carrier_packages = 1
        res = super(StockPicking, self).button_validate()
        return res
