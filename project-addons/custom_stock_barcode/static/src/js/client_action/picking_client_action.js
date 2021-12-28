odoo.define("custom_stock_barcode.picking_client_action", function (require) {
    "use strict";

    var PickingClientAction = require("stock_barcode.picking_client_action");

    PickingClientAction.include({
        custom_events: _.extend(
            {
                "reset_moves": "_onResetMoves",
            },
            PickingClientAction.prototype.custom_events
        ),

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.commands["O-BTN.reset_moves"] = this._resetMoves.bind(this);
        },
        /**
         * @override
         */
        _getPageFields: function () {
            var res = this._super();
            res.push(
                // Parent
                ["location_parent", "location_id.location_id.display_name"],
                ["location_parent_format", "location_id.location_id.loc_format"],
                // Gparent
                [
                    "location_gparent",
                    "location_id.location_id.location_id.display_name",
                ],
                // Parent dest
                ["location_dest_parent", "location_dest_id.location_id.display_name"],
                [
                    "location_dest_parent_format",
                    "location_dest_id.location_id.loc_format",
                ],
                // Gparent dest
                [
                    "location_dest_gparent",
                    "location_dest_id.location_id.location_id.display_name",
                ]
            );
            return res;
        },

        /**
         * Makes the rpc to `button_reset_moves`.
         *
         * @private
         */
        _resetMoves: function () {
            var self = this;
            this.mutex.exec(function () {
                return self._save().then(function () {
                    return self
                        ._rpc({
                            model: self.actionParams.model,
                            method: "button_reset_moves",
                            args: [[self.actionParams.pickingId]],
                            context: self.context,
                        })
                        .then(function (res) {
                            self.do_notify(_t("Reset"), res);
                            self.trigger_up("reload");
                        });
                });
            });
        },

        // --------------------------------------------------------------------------
        // Handlers
        // --------------------------------------------------------------------------

        /**
         * Handles the `reset_moves` OdooEvent. It makes an RPC call
         * to the method 'reset_moves' to reset the done quantities of the picking
         *
         * @private
         * @param {OdooEvent} ev
         */
        _onResetMoves: function (ev) {
            ev.stopPropagation();
            this._resetMoves();
        },
    });
});
