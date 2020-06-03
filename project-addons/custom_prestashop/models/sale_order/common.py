# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.addons.component.core import Component


class PrestashopSaleOrderListener(Component):
    _inherit = "prestashop.sale.order.listener"

    def on_record_write(self, record, fields=None):
        return


class SaleOrde(models.Model):

    _inherit = "sale.order"

    def write(self, vals):
        run = False
        if vals.get("prestashop_state") or vals.get("invoice_status"):
            run = True
        res = super().write(vals)
        if run:
            for workflow in self.mapped("workflow_process_id"):
                self.env["automatic.workflow.job"].run_with_workflow(workflow)
        return res


class PrestashopSaleOrder(models.Model):
    _inherit = "prestashop.sale.order"

    @api.multi
    def write(self, vals):
        can_edit = True
        if (
            "prestashop_order_line_ids" in vals
            and vals["prestashop_order_line_ids"]
        ):
            for picking in self.odoo_id.picking_ids:
                if picking.state in ("done"):
                    can_edit = False
            if not can_edit:
                raise Exception("No se puede editar el pedido.")
            self.odoo_id.picking_ids.filtered(
                lambda r: r.state in ("confirmed", 'assigned')
            ).action_cancel()
            if self.odoo_id.state == "done":
                self.odoo_id.action_unlock()
            self.odoo_id.action_cancel()
        res = super().write(vals)
        if (
            "prestashop_order_line_ids" in vals
            and vals["prestashop_order_line_ids"]
            and can_edit
        ):
            self.odoo_id.action_draft()
            self.odoo_id.action_confirm()
        return res
