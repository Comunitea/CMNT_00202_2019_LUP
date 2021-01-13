# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _



class MrpProduction(models.Model):

    _inherit = "mrp.production"

    @api.multi
    def button_mark_done(self):
        res = super().button_mark_done()
        self.product_id.button_bom_cost()
        return res