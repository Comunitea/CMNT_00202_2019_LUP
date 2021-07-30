# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class PrinterMaintance(models.Model):

    _name = 'printer.maintance'

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', 'Asignar a')
    rule_id = fields.Many2one('printer.maintance.rule', 'Disparador')
    printer_instance_id = fields.Many2one('printer.machine.instance', 'Impresora')
    rule_type = fields.Selection(
        [('hours', 'Por horas de uso'), ('date', 'Por fecha')], 
        'Tipo regla')
    note = fields.Text('Notas')
    hours = fields.Text('Tiempo mantenimiento')
    code = fields.Char('Codigo mantenimiento')
    state = fields.Selection(
        [('pending', 'Pendiente'), ('done', 'Finalizado')], readonly=True, 
        default='pending', copy=False, string="Estado")

    def action_done(self):
        self.ensure_one()
        self.printer_instance_id.write({
            'machine_hours_count': 0,
            'maintance_date': fields.Date.today()
        })
        self.state = 'done'
