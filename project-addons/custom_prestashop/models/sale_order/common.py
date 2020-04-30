# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.addons.component.core import Component


class PrestashopSaleOrderListener(Component):
    _inherit = "prestashop.sale.order.listener"

    def on_record_write(self, record, fields=None):
        return


class SaleOrde(models.Model):

    _inherit = "sale.order"

    prestashop_state = fields.Many2one("sale.order.state")

    def write(self, vals):
        run = False
        if vals.get('prestashop_state') or vals.get('invoice_status'):
            run = True
        res = super().write(vals)
        if run:
            for workflow in self.mapped('workflow_process_id'):
                self.env['automatic.workflow.job'].run_with_workflow(workflow)
        return res
