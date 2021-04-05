# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _order = 'invoice_id, sequence, id'

    summary_line_ids = fields.Many2many(
        'sale.summary.line',
        'sale_summary_line_invoice_rel',
        'invoice_line_id', 'order_summary_line_id',
        string='Sales Summary Lines', readonly=True, copy=False)
        