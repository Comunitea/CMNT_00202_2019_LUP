# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'
    
    check_vies = fields.Boolean(string='Check VIES', help="Only apply fiscal position if VIES  validation is ok")
    