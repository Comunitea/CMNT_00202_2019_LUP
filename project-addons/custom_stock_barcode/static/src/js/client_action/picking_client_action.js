odoo.define("custom_stock_barcode.picking_client_action", function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var PickingClientAction = require("stock_barcode.picking_client_action");

    PickingClientAction.include({
        custom_events: _.extend(
            {
                reset_moves: "_onResetMoves",
                find_product: "_onFindProduct",
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

        /**
         * Finds product on current stock.picking pages.
         *
         * @private
         */
         _findProduct: async function () {
            var self = this;
            this.mutex.exec(function () {
                return self._save().then(function () {
                    return self
                        ._rpc({
                            model: 'stock.picking',
                            method: "button_find_product_line",
                            args: [[self.actionParams.pickingId]],
                            context: self.context,
                        })
                        .then(function (res) {
                            var exitCallback = function () {
                                core.bus.on('barcode_scanned', self, self._onBarcodeScannedHandler);
                            };
                            var options = {
                                on_close: exitCallback,
                            };
                            core.bus.off('barcode_scanned', self, self._onBarcodeScannedHandler);
                            return self.do_action(res, options).then(function() {
                                setTimeout(function () {
                                    var button = $(document).find(".find_line");
                                    $(button).on('click', function () {
                                        var product_id = $(button).closest('div.modal-content').find('a[name="product_id"]').attr('href').replace('#id=', '').replace('&model=product.product', '');
                                        if (product_id && product_id != ''){
                                            var new_index = false;
                                            product_id = parseInt(product_id);
                                            if(self.pages) {
                                                _.each(self.pages, function (v, k){
                                                    _.each(v.lines, function (line_v, line_k){
                                                        if (line_v.product_id.id == product_id) {
                                                            new_index = k
                                                            return false;
                                                        }
                                                    });
                                                });
                        
                                                if (new_index) {
                                                    self.currentPageIndex = new_index;
                                                    self._reloadLineWidget(self.currentPageIndex);
                                                    self._endBarcodeFlow();
                                                }
                                            }       
                                        }
                                        $(button).closest('div.modal-content').find('button.close').trigger("click");
                                    });
                                }, 100);
                            });
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
        _onFindProduct: function (ev) {
            ev.stopPropagation();
            this._findProduct();
        },
    });
});
