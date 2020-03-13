# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    cost_sheet_id = fields.Many2one('cost.sheet', 'Cost Sheet')