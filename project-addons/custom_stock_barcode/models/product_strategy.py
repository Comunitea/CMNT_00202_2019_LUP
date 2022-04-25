# © 2022 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api

class FixedPutAwayStrategy(models.Model):
    _inherit = 'stock.fixed.putaway.strat'

    max_qty = fields.Integer('Max. quantity', help="Max quantity for this product on this location.")
