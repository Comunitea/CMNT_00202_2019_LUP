# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class ResPartner(models.Model):

    _inherit = "res.partner"

    admin_fact = fields.Float('Factor administrativo (%)')
    require_num_order = fields.Boolean('Requires num order')
    supplier_number = fields.Char('Supplier Number')
    
    @api.multi
    def _get_admin_fact(self):
        if self.parent_id and self.parent_id.admin_fact:
            return self.parent_id.admin_fact
        else:
            return self.commercial_partner_id.admin_fact