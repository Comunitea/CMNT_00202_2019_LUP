# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


PRINT_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS P396'),
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('sls2', 'SLS'),
    ('dmls', 'DMLS'),
]


class PrinterMachine(models.Model):

    _name = 'printer.machine'
    _description = "Impresora"

    name = fields.Char('Name')
    type = fields.Selection(PRINT_TYPES, 'Print Type', required=True)
    routing_id = fields.Many2one('mrp.routing', 'Routing', required=True)

    diameter = fields.Float('Diameter')
    machine_hour = fields.Float('H hombre / H maquina', digits=(16, 9))
    euro_hour = fields.Float('Euro hour')
    discount = fields.Float('Max disacount')
    discount2 = fields.Float('Discount 2º unit')
    max_disc_qty = fields.Float('Max discount quantity')

    default_fdm = fields.Boolean('Por defecto en fdm')
    default_sls = fields.Boolean('Por defecto en sl P396')
    default_sls2 = fields.Boolean('Por defecto en sls')
    default_poly = fields.Boolean('Por defecto en poly')
    default_sla = fields.Boolean('Por defecto en sla')
    default_dmls = fields.Boolean('Por defecto en dmls')

    perfil_ids = fields.One2many('sheet.perfil', 'printer_id', 'Perfiles')
    printer_ids = fields.One2many(
        'printer.machine.instance', 'categ_id', 'Impresoras')

    _sql_constraints = [(
        'default_fdm_unique',
        'unique(default_fdm)',
        'Ya existe otra impresora por defecto para FDM'
        ),
        (
        'default_sls_unique',
        'unique(default_sls)',
        'Ya existe otra impresora por defecto para SLS P396'
        ),
        (
        'default_sls2_unique',
        'unique(default_sls2)',
        'Ya existe otra impresora por defecto para SLS'
        ),
        (
        'default_poly_unique',
        'unique(default_poly)',
        'Ya existe otra impresora por defecto para POLY'
        ),
        (
        'default_sla_unique',
        'unique(default_sla)',
        'Ya existe otra impresora por defecto para SLA'
        ),
        (
        'default_dmls_unique',
        'unique(default_dmls)',
        'Ya existe otra impresora por defecto para DMLS'
        )
    ]


class PrinterMachineInstance(models.Model):

    _name = 'printer.machine.instance'
    _description = "Categoría Impresora"

    name = fields.Char('Name')
    categ_id = fields.Many2one('printer.machine', 'Categoría Impresora')
    machine_hours = fields.Float('Horas máquina totales')
    rule_ids = fields.One2many(
        'printer.maintance.rule', 'printer_instance_id',
        'Reglas mantenimiento')
    maintance_ids = fields.One2many(
        'printer.maintance', 'printer_instance_id',
        'Mantenimientos')
    maintances_count = fields.Integer('# Maintances',
                                      compute='_get_maintances_count')

    def update_hours(self, hours):
        self.ensure_one()
        mh = self.machine_hours
        self.write({
            'machine_hours':  mh + hours,
        })

    @api.model
    def check_maintance_rules(self):
        domain = [('rule_ids', '!=', False)]
        printers = self.env['printer.machine.instance'].search(domain)
        for p in printers:
            for rule in p.rule_ids:
                if rule.check():
                    rule.run_maintance()

    @api.multi
    def _get_maintances_count(self):
        for p in self:
            p.maintances_count = len(p.maintance_ids)

    @api.multi
    def view_maintances(self):
        self.ensure_one()
        maintances = self.maintance_ids
        action = self.env.ref(
            'cost_sheet_lupeon.action_printer_maintances').read()[0]
        action['context'] = {'search_default_my_maintances': 0}
        if len(maintances) > 1:
            action['domain'] = [('id', 'in', maintances.ids)]
        elif len(maintances) == 1:
            form_view_name = 'printer.maintance.view'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = maintances.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class PrinterMaintanceRule(models.Model):

    _name = 'printer.maintance.rule'
    _description = "Regla mantenimiento"
    _rec_name = 'code'

    printer_instance_id = fields.Many2one(
        'printer.machine.instance', 'Impresora', required=True)
    rule_type = fields.Selection(
        [('hours', 'Por horas de uso'), ('date', 'Por fecha')], 
        'Tipo regla')
    value = fields.Float('Intervalo mantenimientos')
    value_hours = fields.Float('Horas próximo mantenimiento')
    value_date = fields.Date('Fecha próximo mantenimiento')
    code = fields.Char('Codigo mantenimiento')
    user_id = fields.Many2one('res.users', 'Asignar a')

    def check(self):
        self.ensure_one()
        print('check')
        res = False
        printer = self.printer_instance_id

        # Compruebo que esta regla no esté pendiente
        domain = [
            ('rule_id', '=', self.id),
            ('state', '!=', 'done'),
            ('printer_instance_id', '=', printer.id),
        ]
        pending_maintances = self.env['printer.maintance'].search(domain)
        if pending_maintances:
            return False

        if self.rule_type == 'hours':
            if printer.machine_hours >= self.value_hours:
                res = True
        else:
            if self.value_date:
                today = fields.Date.today()
                mdate = self.value_date
                if today >= mdate:
                    res = True
            else:
                res = True

        return res

    def run_maintance(self):
        self.ensure_one()
        print('run')
        printer = self.printer_instance_id
        vals = {
            'name': 'Mantenimiento %s para %s' % (self.code or '', printer.name),
            'user_id': self.user_id.id,
            'printer_instance_id': printer.id,
            'rule_type': self.rule_type,
            'code': self.code,
            'rule_id': self.id
        }
        self.env['printer.maintance'].create(vals)
