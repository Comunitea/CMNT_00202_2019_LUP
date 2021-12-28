odoo.define("custom_stock_barcode.MainMenu", function (require) {
    "use strict";

    var MainMenu = require("stock_barcode.MainMenu").MainMenu;

    MainMenu.include({
        events: _.extend(
            {
                "click .button_productions": "_onClickOpenProductions",
            },
            MainMenu.prototype.events
        ),
        init: function (parent, action) {
            this._super.apply(this, arguments);
        },
        _onClickOpenProductions: function () {
            this.do_action("custom_stock_barcode.mrp_production_action_kanban");
        },
    });
});
