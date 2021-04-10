# Copyright 2021 Comunitea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class CheckSendPrintWiz(models.TransientModel):
    _name = 'check.send.print.wiz'
    _description = "Check Send Print Wizard"


    exception_msg = fields.Text(readonly=True)
    order_id = fields.Many2one('sale.order', 'Pedido')
    continue_method = fields.Char()

    @api.multi
    def action_show(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Revisar presupuesto'),
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def button_continue(self):
        self.ensure_one()
        return getattr(self.order_id.with_context(bypass_checks=True), self.continue_method)()
