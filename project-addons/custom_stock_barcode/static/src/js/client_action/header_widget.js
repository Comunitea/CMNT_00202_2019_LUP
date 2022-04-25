odoo.define("custom_stock_barcode.HeaderWidget", function (require) {
    "use strict";

    require("web.dom_ready");
    var core = require("web.core");
    var QWeb = core.qweb;
    var HeaderWidget = require("stock_barcode.HeaderWidget");

    HeaderWidget.include({
        events: _.extend(
            {
                "click .o_find_product": "_onClickFindProduct",
            },
            HeaderWidget.prototype.events
        ),

        init: function (parent, model, mode, allow_scrap) {
            this._super.apply(this, arguments);
        },

        // --------------------------------------------------------------------------
        // Handlers
        // --------------------------------------------------------------------------

        /**
         * Handles the click on the `reset moves`.
         *
         * @private
         * @param {MouseEvent} ev
         */
         _onClickFindProduct: function (ev) {
            ev.stopPropagation();
            this.trigger_up("find_product");
        },
    });
});
