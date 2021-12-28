# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_type = fields.Selection(related="product_id.type")
    virtual_available_at_date = fields.Float(compute="_compute_qty_at_date")
    scheduled_date = fields.Datetime(compute="_compute_qty_at_date")
    free_qty_today = fields.Float(compute="_compute_qty_at_date")
    qty_available_today = fields.Float(compute="_compute_qty_at_date")
    warehouse_id = fields.Many2one("stock.warehouse", compute="_compute_qty_at_date")
    qty_to_recieve = fields.Float(compute="_compute_qty_to_recieve")
    is_mto = fields.Boolean(default=False)
    display_qty_widget = fields.Boolean(compute="_compute_qty_to_recieve")
    real_stock = fields.Float("Real stock", related="product_id.qty_available")

    @api.depends("product_id", "product_uom_qty", "qty_received", "state")
    def _compute_qty_to_recieve(self):
        """Based on _compute_qty_to_deliver method of sale.order.line
        model in Odoo v13 'sale_stock' module.
        """
        for line in self:
            line.qty_to_recieve = line.product_uom_qty - line.qty_received
            line.display_qty_widget = (
                line.state == "draft"
                and line.product_type == "product"
                and line.qty_to_recieve > 0
            )

    @api.depends(
        "product_id",
        "product_uom_qty",
        "orderpoint_id.warehouse_id",
        "order_id.date_planned",
    )
    def _compute_qty_at_date(self):
        """Based on _compute_free_qty method of sale.order.line
        model in Odoo v13 'sale_stock' module.
        """
        qty_processed_per_product = defaultdict(lambda: 0)
        grouped_lines = defaultdict(lambda: self.env["purchase.order.line"])
        now = fields.Datetime.now()
        for line in self.sorted(key=lambda r: r.sequence):
            if not line.display_qty_widget:
                continue
            line.warehouse_id = line.orderpoint_id.warehouse_id
            if line.order_id.date_planned:
                date = line.order_id.date_planned
            else:
                if line.order_id.state in ["purchase", "done"]:
                    confirm_date = line.order_id.date_order
                else:
                    confirm_date = now
                date = confirm_date
            grouped_lines[(line.warehouse_id.id, date)] |= line
        treated = self.browse()
        for (warehouse, scheduled_date), lines in grouped_lines.items():
            for line in lines:
                product = line.product_id.with_context(
                    to_date=scheduled_date, warehouse=warehouse
                )
                qty_available = product.qty_available
                free_qty = product.free_qty
                virtual_available = product.virtual_available
                qty_processed = qty_processed_per_product[product.id]
                line.scheduled_date = scheduled_date
                line.qty_available_today = qty_available - qty_processed
                line.free_qty_today = free_qty - qty_processed
                virtual_available_at_date = virtual_available - qty_processed
                line.virtual_available_at_date = virtual_available_at_date
                qty_processed_per_product[product.id] += line.product_uom_qty
            treated |= lines
        remaining = self - treated
        remaining.write(
            {
                "virtual_available_at_date": False,
                "scheduled_date": False,
                "free_qty_today": False,
                "qty_available_today": False,
                "warehouse_id": False,
            }
        )
