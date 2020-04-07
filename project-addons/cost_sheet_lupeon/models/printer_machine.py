# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

PRINT_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS'),
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('dmls', 'DMLS'),
]

class PrinterMachine(models.Model):

    _name = 'printer.machine'

    name = fields.Char('Name')
    type = fields.Selection(PRINT_TYPES, 'Print Type')

    diameter = fields.Float('Diameter')
    machine_hour = fields.Float('H hombre / H maquina', digits=(16, 9))
    euro_hour = fields.Float('Euro hour')
    discount = fields.Float('Max disacount')
    discount2 = fields.Float('Discount 2º unit')
    max_disc_qty = fields.Float('Max discount quantity')
