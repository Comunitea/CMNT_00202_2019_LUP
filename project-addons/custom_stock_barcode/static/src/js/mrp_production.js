odoo.define("custom_stock_barcode.production_kanban", function (require) {
    "use strict";

    var KanbanRecord = require("web.KanbanRecord");

    KanbanRecord.include({
        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _openRecord: function () {
            if (this.modelName === "mrp.production") {
                this.$("button").first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});
