# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    label_printed = fields.Boolean('Label printed')

    def get_label_url(self):
        """
        Return static url of production workorders
        %23 = #
        %26 = &
        """
        self.ensure_one()
        res = ""
        res += "https://erp.dativic.com/"
        res += "web%23id={}%26action=472".format(str(self.id))
        res += "%26model=mrp.production%26view_type=form%26menu_id=299"
        print(res)
        return res

    def print_label(self):
        self.write({'label_printed': True})
        return self.env.ref('custom_documents_lupeon.report_production_label').\
            report_action(self)
