# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class MrpProductionMoveWzd(models.TransientModel):
    _name = "mrp.production.move.wzd"

    @api.model
    def _get_default_raw_material_production_id(self):
        return self._context.get("raw_material_production_id", False)

    @api.model
    def _get_default_location_id(self):
        return self._context.get("location_id", False)

    @api.model
    def _get_default_location_dest_id(self):
        return self._context.get("location_dest_id", False)

    @api.model
    def _get_default_product_id(self):
        return self._context.get("product_id", False)

    @api.model
    def _get_default_product_uom(self):
        return self._context.get("product_uom", False)

    raw_material_production_id = fields.Many2one(
        "mrp.production",
        "Production Order for finished products",
        default=lambda self: self._get_default_raw_material_production_id(),
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        default=lambda self: self._get_default_product_id(),
    )
    location_id = fields.Many2one(
        "stock.location",
        "Location",
        default=lambda self: self._get_default_location_id(),
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        string="Location",
        default=lambda self: self._get_default_location_dest_id(),
    )
    product_uom = fields.Many2one(
        "uom.uom",
        "Unit of Measure",
        default=lambda self: self._get_default_product_uom(),
    )
    product_uom_qty = fields.Float(
        "Quantity", digits=dp.get_precision("Product Unit of Measure"), default=1
    )

    def confirm(self):
        try:
            move = self.env["stock.move"].create(
                {
                    "raw_material_production_id": self.raw_material_production_id.id,
                    "location_id": self.location_id.id,
                    "location_dest_id": self.location_dest_id.id,
                    "product_id": self.product_id.id,
                    "name": self.product_id.partner_ref,
                    "product_uom_qty": self.product_uom_qty,
                    "product_uom": self.product_uom.id,
                    "state": "waiting",
                }
            )
            move.raw_material_production_id.action_assign()
            return True
        except Exception as e:
            _logger.warning("Error trying to create move: {}".format(e))
            return False
