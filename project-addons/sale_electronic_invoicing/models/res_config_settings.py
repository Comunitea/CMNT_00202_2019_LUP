# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    eic_payment_mode_id = fields.Many2one(related='company_id.eic_payment_mode_id',
                                string='Modo de pago para facturación electrónica',
                                readonly=False)
    eic_payment_term_id = fields.Many2one(related='company_id.eic_payment_term_id', 
                                string='Plazo de pago para facturación electrónica', 
                                readonly=False)
    