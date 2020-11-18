# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def get_label_url(self):
        """
        Return static url of production workorders
        %23 = #
        %26 = &
        """
        self.ensure_one()
        res = ""
        res += "https://erp.dativic.com/"
        res += "web%23action=456%26active_id={}".format(str(self.id))
        res += "%26model=mrp.workorder%26view_type=list%26menu_id=183"
        print(res)
        return res
