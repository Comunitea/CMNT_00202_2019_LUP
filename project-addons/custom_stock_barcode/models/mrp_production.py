# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_production_fields_to_read(self):
        """Return the default fields to read from the picking."""
        return [
            "move_raw_ids",
            "picking_type_id",
            "location_src_id",
            "location_dest_id",
            "name",
            "state",
            "ok_tech",
            "availability",
            "is_locked",
            "routing_id",
            "check_to_done",
            "company_id",
            "all_wo_done",
        ]

    def get_barcode_view_state(self):
        """Return the initial state of the barcode view as a dict."""
        fields_to_read = self._get_production_fields_to_read()
        productions = self.read(fields_to_read)

        for production in productions:
            move_raw_ids = self.env["stock.move"].browse(production.pop("move_raw_ids"))
            production["move_raw_ids"] = move_raw_ids.mapped(
                "active_move_line_ids"
            ).read(
                [
                    "product_id",
                    "location_id",
                    "location_dest_id",
                    "qty_done",
                    "display_name",
                    "product_uom_qty",
                    "product_uom_id",
                    "product_barcode",
                    "owner_id",
                    "lot_id",
                    "lot_name",
                    "package_id",
                    "result_package_id",
                    "dummy_id",
                ]
            )

            if any(len(x.active_move_line_ids) == 0 for x in move_raw_ids):
                production["quantity_not_available"] = True
            else:
                production["quantity_not_available"] = False
            # Prefetch data
            product_ids = tuple(
                {
                        move_line_id["product_id"][0]
                        for move_line_id in production["move_raw_ids"]
                }
            )
            tracking_and_barcode_per_product_id = {}
            for res in (
                self.env["product.product"]
                .with_context(active_test=False)
                .search_read([("id", "in", product_ids)], ["tracking", "barcode"])
            ):
                tracking_and_barcode_per_product_id[res.pop("id")] = res

            for move_line_id in production["move_raw_ids"]:
                id = move_line_id.pop("product_id")[0]
                move_line_id["product_id"] = {
                    "id": id,
                    **tracking_and_barcode_per_product_id[id],
                }
                id, name = move_line_id.pop("location_id")
                move_line_id["location_id"] = {"id": id, "display_name": name}
                id, name = move_line_id.pop("location_dest_id")
                move_line_id["location_dest_id"] = {"id": id, "display_name": name}
            id, name = production.pop("location_src_id")
            production["location_id"] = self.env["stock.location"].search_read(
                [("id", "=", id)], ["parent_path"]
            )[0]
            production["location_id"].update({"id": id, "display_name": name})
            id, name = production.pop("location_dest_id")
            production["location_dest_id"] = self.env["stock.location"].search_read(
                [("id", "=", id)], ["parent_path"]
            )[0]
            production["location_dest_id"].update({"id": id, "display_name": name})
            # company_id
            id, name = production.pop("company_id")
            production["company_id"] = {"id": id, "display_name": name}
            production["group_stock_multi_locations"] = self.env.user.has_group(
                "stock.group_stock_multi_locations"
            )
            production["group_tracking_owner"] = self.env.user.has_group(
                "stock.group_tracking_owner"
            )
            production["group_tracking_lot"] = self.env.user.has_group(
                "stock.group_tracking_lot"
            )
            production["group_production_lot"] = self.env.user.has_group(
                "stock.group_production_lot"
            )
            production["group_uom"] = self.env.user.has_group("uom.group_uom")
            production["picking_type_code"] = (
                self.env["stock.picking.type"]
                .browse(production["picking_type_id"][0])
                .code
            )
            production["use_create_lots"] = (
                self.env["stock.picking.type"]
                .browse(production["picking_type_id"][0])
                .use_create_lots
            )
            production["use_existing_lots"] = (
                self.env["stock.picking.type"]
                .browse(production["picking_type_id"][0])
                .use_existing_lots
            )
            production["show_entire_packs"] = (
                self.env["stock.picking.type"]
                .browse(production["picking_type_id"][0])
                .show_entire_packs
            )
            production["actionReportDeliverySlipId"] = self.env.ref(
                "stock.action_report_delivery"
            ).id
            if self.env.user.company_id.nomenclature_id:
                production["nomenclature_id"] = [
                    self.env.user.company_id.nomenclature_id.id
                ]
        return productions

    def open_production(self):
        """method to open the form view of the current record
        from a button on the kanban view
        """
        self.ensure_one()
        view_id = self.env.ref("mrp.mrp_production_form_view").id
        return {
            "name": _("Open production form"),
            "res_model": "mrp.production",
            "view_type": "form",
            "view_mode": "form",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": self.id,
        }

    def open_production_client_action(self):
        """method to open the form view of the current record
        from a button on the kanban view
        """
        self.ensure_one()
        use_form_handler = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_barcode.use_form_handler")
        )
        if use_form_handler:
            view_id = self.env.ref("mrp.mrp_production_form_view").id
            return {
                "name": _("Open production form"),
                "res_model": "mrp.production",
                "view_type": "form",
                "view_mode": "form",
                "view_id": view_id,
                "type": "ir.actions.act_window",
                "res_id": self.id,
            }
        else:
            action = self.env.ref(
                "custom_stock_barcode.stock_barcode_production_client_action"
            ).read()[0]
            params = {
                "model": "mrp.production",
                "production_id": self.id,
                "ok_tech": self.ok_tech,
                "availability": self.availability,
                "is_locked": self.is_locked,
                "company_id": self.company_id,
                "all_wo_done": self.all_wo_done,
                "state": self.state,
                "routing_id": self.routing_id,
                "check_to_done": self.check_to_done,
                "nomenclature_id": [self.env.user.company_id.nomenclature_id.id],
            }
            res = dict(action, target="fullscreen", params=params)
            return res
