# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    cost_sheet_sale = fields.Boolean(related='company_id.cost_sheet_sale', string='Sale without Cost Sheets', readonly=False)
    