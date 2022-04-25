odoo.define("custom_stock_barcode.ClientAction", function (require) {
    "use strict";

    var core = require("web.core");
    var _t = core._t;
    var ClientAction = require("stock_barcode.ClientAction");

    var cache = {};

    ClientAction.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.actionParams = {
                pickingId: action.params.picking_id,
                inventoryId: action.params.inventory_id,
                productionId: action.params.production_id,
                model: action.params.model,
            };
            this.line_check = null;
            this.productsByDefaultCodes = [];
            this.productsByProviderCodes = [];
        },
        willStart: function () {
            /* There is no recordId because there is no productionId. */
            /* So if the model is mrp.production we need to set it.  */
            var self = this;
            self._getProductDefaultCodes();
            self._getProductProviderCodes();
            return this._super();
        },
        _step_product: function (barcode, linesActions) {
            var self = this;
            var errorMessage = false;
            this._isProduct(barcode).then(function (product_check) {
                if (product_check) {
                    self.line_check = self._findCandidateLineToIncrement({
                        product: product_check,
                        barcode: barcode,
                    });
                    if (!self.line_check || !self.line_check.id) {
                        errorMessage = _t("Product not found, opening wizard");
                        return self
                            ._rpc({
                                model: 'stock.picking',
                                method: "button_add_product_line",
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
                                        var button = $(document).find(".add_line");
                                        $(button).on('click', function () {
                                            var res = self._incrementLines({'product': product_check, 'barcode': barcode});
                                            if (res.isNewLine) {
                                                if (self.actionParams.model === 'stock.inventory') {
                                                    // FIXME sle: add owner_id, prod_lot_id, owner_id, product_uom_id
                                                    return self._rpc({
                                                        model: 'product.product',
                                                        method: 'get_theoretical_quantity',
                                                        args: [
                                                            res.lineDescription.product_id.id,
                                                            res.lineDescription.location_id.id,
                                                        ],
                                                    }).then(function (theoretical_qty) {
                                                        res.lineDescription.theoretical_qty = theoretical_qty;
                                                        linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                                                        self.scannedLines.push(res.id || res.virtualId);
                                                        return $.when({linesActions: linesActions});
                                                    });
                                                } else {
                                                    linesActions.push([self.linesWidget.addProduct, [res.lineDescription, self.actionParams.model]]);
                                                }
                                            } else {
                                                if (product.tracking === 'none') {
                                                    linesActions.push([self.linesWidget.incrementProduct, [res.id || res.virtualId, product.qty || 1, self.actionParams.model]]);
                                                } else {
                                                    linesActions.push([self.linesWidget.incrementProduct, [res.id || res.virtualId, 0, self.actionParams.model]]);
                                                }
                                            }
                                            self.scannedLines.push(res.id || res.virtualId);
                                            $(button).closest('div.modal-content').find('button.close').trigger("click");
                                            self.trigger_up("reload");
                                        });
                                    }, 100);
                                });
                            });
                    }
                }
            });

            if (errorMessage) {
                return $.Deferred().reject(errorMessage);
            }
            return self._super(barcode, linesActions);
        },
        _getProductByBarcode: function (barcode) {
            if (this.productsByDefaultCodes[barcode]) {
                return $.when(this.productsByDefaultCodes[barcode]);
            } else if (this.productsByProviderCodes[barcode]) {
                return $.when(this.productsByProviderCodes[barcode]);
            }

            return this._super(barcode);
        },
        /**
         * Make an rpc to get the products default codes and afterwards set `this.productsByDefaultCodes`.
         *
         * @private
         * @returns {Deferred}
         */
        _getProductDefaultCodes: function () {
            var self = this;

            if (cache.productsByDefaultCodes) {
                self.productsByDefaultCodes = cache.productsByDefaultCodes;
                return $.when();
            }

            return this._rpc({
                model: "product.product",
                method: "get_all_products_by_default_code",
                args: [[]],
            }).then(function (res) {
                self.productsByDefaultCodes = res;
                cache.productsByDefaultCodes = res;
            });
        },
        /**
         * Make an rpc to get the products provider codes and afterwards set `this.productsByProviderCodes`.
         *
         * @private
         * @returns {Deferred}
         */
        _getProductProviderCodes: function () {
            var self = this;

            if (cache.productsByProviderCodes) {
                self.productsByProviderCodes = cache.productsByProviderCodes;
                return $.when();
            }

            return this._rpc({
                model: "product.product",
                method: "get_all_products_by_provider_code",
                args: [[]],
            }).then(function (res) {
                self.productsByProviderCodes = res;
                cache.productsByProviderCodes = res;
            });
        },

    });
});
