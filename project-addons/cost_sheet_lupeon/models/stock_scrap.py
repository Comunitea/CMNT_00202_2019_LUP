# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockScrap(models.Model):

    _inherit = "stock.scrap"

    machine_hours = fields.Float('Tiempo máquina', required=True)

    def action_validate(self):
        res = super().action_validate()
        # if not self.machine_hours and not self._context.get('ok_check', False):
        #     raise UserError('Es necesario indicar el tiempo máquina')
        if self.workorder_id:
            vals = {
                'workorder_id': self.workorder_id.id,
                'time': self.machine_hours
            }
            self.env['machine.time'].create(vals)
        return res
