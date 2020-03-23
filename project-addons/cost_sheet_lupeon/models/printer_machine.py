# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

PRINT_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS'),
    ('Poly', 'Poly'),
    ('sla', 'SLA'),
    ('dmls', 'DMLS'),
]

class PrinterMachine(models.Model):

    _name = 'printer.machine'

    name = fields.Char('Sector')
    type = fields.Selection(PRINT_TYPES, 'Print Type')
