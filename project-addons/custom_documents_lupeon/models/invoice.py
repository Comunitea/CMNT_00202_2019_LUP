# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    report_tech = fields.Char('Technology')
    report_material = fields.Char('Material')
    report_finish = fields.Char('Finish')
    model_image = fields.Binary('Model image')
    ref = fields.Char('Reference')
    
 