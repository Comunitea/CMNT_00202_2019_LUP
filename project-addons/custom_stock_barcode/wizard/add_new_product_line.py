# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AddProductLine(models.TransientModel):
    _name = "add.product.line"
    _description = "Wizard to scan SN/LN for specific product"
