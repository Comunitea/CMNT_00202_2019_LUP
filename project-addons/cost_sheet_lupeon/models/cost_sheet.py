# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

LEGISLATION_SEL = [
    ('automotive', 'Automotive'),
    ('feeding', 'Feeding'),
    ('sanitary', 'Sanitary'),
    ('aeronautical', 'Aeronautical'),
    ('others', 'Others'),
]

class CostSheet(models.Model):

    _name = 'cost.sheet'

    name = fields.Char('Name')

    init_cost = fields.Float('Init Cost')
    admin_fact = fields.Float('Administrative factor')
    disc_qty = fields.Float('Administrative factor')
    disc2 = fields.Float('Administrative factor')
    increment = fields.Float('Increment')
    inspection_type = fields.Selection(
        [('visual', 'Visual'), ('visual', 'Visual')])


    # DISEÑO
    design_ref = fields.Char('Design Reference')
    flat_ref = fields.Char('Flat ref')
    legislation = fields.Selection(LEGISLATION_SEL, 'Legislation applicable')
    time_line_ids = fields.One2many('design.time.line', 'sheet_id', 'Times')
    description = fields.Text('Technical Requisist')
    customer_note = fields.Text('Customer Coments')



class DesignTimeLine(models.Model):

    _name = 'design.time.line'

    sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    name = fields.Char('Software name')
    hours = fields.Float('Hours')
    price_hour = fields.Float('Price Hour')
    hours = fields.Float('Discount')
    hours = fields.Float('Total')
    