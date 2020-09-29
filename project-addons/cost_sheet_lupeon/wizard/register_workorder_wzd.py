
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RegisterWorkorderWizard(models.TransientModel):
    _name = "register.workorder.wizard"

    @api.model
    def default_get(self, default_fields):
        wo = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        res = super().default_get(default_fields)
        res['qty'] = wo.qty_producing
        return res

    qty = fields.Float('Cantidad hecha', required=True)
    machine_hours = fields.Float('Horas máquina')

    def confirm(self):
        wo = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        wo.qty_producing = self.qty

        if self.machine_hours:
            vals = {
                'workorder_id': wo.id,
                'time': self.machine_hours
            }
            self.env['machine.time'].create(vals)
        wo.record_production()
        return
