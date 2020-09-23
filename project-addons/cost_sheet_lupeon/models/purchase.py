# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    dest_sale_id = fields.Many2one('sale.order', 'Project', readonly=True,
                                   copy=False)