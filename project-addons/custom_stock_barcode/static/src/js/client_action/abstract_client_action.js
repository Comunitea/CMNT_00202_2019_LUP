odoo.define('custom_stock_barcode.ClientAction', function (require) {
    'use strict';

    var core = require('web.core');
    var _t = core._t;
    var ClientAction = require('stock_barcode.ClientAction');

    ClientAction.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.product_check = null;
            this.line_check = null;
            this.productsByDefaultCodes = [];
            this.productsByProviderCodes = []
        },
        willStart: function () {
            var self = this;
            self._getProductDefaultCodes();
            self._getProductProviderCodes();
            return this._super();
        },
        _step_product: function (barcode, linesActions) {  
            var errorMessage;          
            this.product_check = this._isProduct(barcode);
            if (this.product_check) {
                this.line_check = this._findCandidateLineToIncrement({'product': this.product_check, 'barcode': barcode});
                if (!this.line_check) {
                    var r = confirm(_t("The scanned product is not in the picking, would you like to add it?"));
                    if (r!= true) {
                        errorMessage = _t("Product addition cancelled");
                        return $.Deferred().reject(errorMessage);
                    }
                }
            }
            return this._super(barcode, linesActions);
        },
        _isProduct: function (barcode) {
            var res = this._super(barcode);
            if (!res) {
                if (this.productsByDefaultCodes[barcode]) {
                    return this.productsByDefaultCodes[barcode];
                } else if (this.productsByProviderCodes[barcode]) {
                    return this.productsByProviderCodes[barcode];
                }
            }
            return res;
        },
        /**
         * Make an rpc to get the products default codes and afterwards set `this.productsByDefaultCodes`.
         *
         * @private
         * @return {Deferred}
         */
        _getProductDefaultCodes: function () {
            var self = this;
            return this._rpc({
                'model': 'product.product',
                'method': 'get_all_products_by_default_code',
                'args': [[]],
            }).then(function (res) {
                self.productsByDefaultCodes = res;
            });
        },
        /**
         * Make an rpc to get the products provider codes and afterwards set `this.productsByProviderCodes`.
         *
         * @private
         * @return {Deferred}
         */
        _getProductProviderCodes: function () {
            var self = this;
            return this._rpc({
                'model': 'product.product',
                'method': 'get_all_products_by_provider_code',
                'args': [[]],
            }).then(function (res) {
                self.productsByProviderCodes = res;
            });
        },
    });

});