odoo.define("custom_stock_barcode.ClientAction", function (require) {
    "use strict";

    var core = require("web.core");
    var _t = core._t;
    var ClientAction = require("stock_barcode.ClientAction");

    var cache = {};

    ClientAction.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.line_check = null;
            this.productsByDefaultCodes = [];
            this.productsByProviderCodes = [];
        },
        willStart: function () {
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
                        var r = confirm(
                            _t(
                                "The scanned product is not in the picking, would you like to add it?"
                            )
                        );
                        if (r == false) {
                            errorMessage = _t("Product addition cancelled");
                        }
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
