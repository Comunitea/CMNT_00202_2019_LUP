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
        },
        _step_product: function (barcode, linesActions) {  
            var errorMessage;          
            this.product_check = this._isProduct(barcode);
            if (this.product_check) {
                this.line_check = this._findCandidateLineToIncrement({'product': this.product_check, 'barcode': barcode});
                if (!this.line_check) {
                    var r = confirm("El producto no se encuentra en el albarán, ¿introducirlo igualmente?");
                    if (r!= true) {
                        errorMessage = "Cancelada introducción del producto.";
                        return $.Deferred().reject(errorMessage);
                    }
                }
            }
            return this._super(barcode, linesActions);
        },
    });

});