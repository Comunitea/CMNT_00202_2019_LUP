odoo.define("custom_stock_barcode.SettingsWidget", function (require) {
    "use strict";

    require("web.dom_ready");
    var core = require("web.core");
    var QWeb = core.qweb;
    var SettingsWidget = require("stock_barcode.SettingsWidget");

    SettingsWidget.include({
        events: _.extend(
            {
                "click .o_reset_moves": "_onClickResetMoves",
                "click .o_mark_as_done": "_onClickMarkAsDone",
                /* Mrp */
                "click .print_flabel": "_onClickPrintFinishedLabel",
                "click .print_production": "_onClickPrintProduction",
                "click .production_scrap": "_onClickProductionScrap",
                "click .create_incident": "_onClickCreateIncident",
            },
            SettingsWidget.prototype.events
        ),

        init: function (parent, model, mode, allow_scrap) {
            this._super.apply(this, arguments);
            this.ok_tech = parent.currentState.ok_tech || false;
            this.availability = parent.currentState.availability || false;
            this.is_locked = parent.currentState.is_locked || false;
            this.state = parent.currentState.state || false;
            this.routing_id = parent.currentState.routing_id || false;
            this.check_to_done = parent.currentState.check_to_done || false;
            this.company_id = parent.currentState.company_id || false;
            this.all_wo_done = parent.currentState.all_wo_done || false;
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
        _onClickResetMoves: function (ev) {
            ev.stopPropagation();
            this.trigger_up("reset_moves");
        },

        _onClickMarkAsDone: function (ev) {
            ev.stopPropagation();
            this.trigger_up("mark_as_done");
        },

        _onClickPrintFinishedLabel: function (ev) {
            ev.stopPropagation();
            this.trigger_up("print_flabel");
        },

        _onClickPrintProduction: function (ev) {
            ev.stopPropagation();
            this.trigger_up("print_production");
        },

        _onClickProductionScrap: function (ev) {
            ev.stopPropagation();
            this.trigger_up("production_scrap");
        },

        _onClickCreateIncident: function (ev) {
            ev.stopPropagation();
            this.trigger_up("create_incident");
        },
    });
});
