# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.addons.component.core import Component


class PrestashopSaleOrderListener(Component):
    _inherit = "prestashop.sale.order.listener"

    def on_record_write(self, record, fields=None):
        return


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def bypass_vies_fpos_check(self):
        res = super().bypass_vies_fpos_check()
        if self.prestashop_bind_ids:
            return True
        return res

    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        if not self._context.get('bypass_vies_fpos_check'):
            return super().onchange_partner_shipping_id()

    @api.onchange('payment_mode_id')
    def onchange_payment_mode_id(self):
        if self.payment_mode_id.default_payment_term_id:
            self.payment_term_id = self.payment_mode_id.default_payment_term_id

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
            self.odoo_id.ignore_exception = True
            self.odoo_id.action_confirm()
        return res


class PrestashopSaleOrderLine(models.Model):
    _inherit = 'prestashop.sale.order.line'

    @api.multi
    def unlink(self):
        if self.odoo_id:
            self.odoo_id.unlink()
        return super().unlink()
