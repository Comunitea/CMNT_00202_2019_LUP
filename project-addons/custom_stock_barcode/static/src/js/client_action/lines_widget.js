odoo.define("custom_stock_barcode.LinesWidget", function (require) {
    "use strict";

    var core = require("web.core");
    var QWeb = core.qweb;
    var ClientAction = require('stock_barcode.LinesWidget');
    var ProductLineSplitModal = require('custom_stock_barcode.ProductLineSplitModal');
    var ProductIncomingLineSplitModal = require('custom_stock_barcode.ProductIncomingLineSplitModal');

    ClientAction.include({
        events: _.extend({}, ClientAction.prototype.events, {
            "click .o_mark_as_done_page": "_onClickMarkAsDone",
            "click .o_ok_quality_page": "_onClickOkQuality",
            "click .o_button_assign": "_onClickButtonAssign",
        }),

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.ProductLineSplitModal = false;
            this.ProducIncomingLineSplitModal = false;
            this.ok_tech = parent.currentState.ok_tech || false;
            this.availability = parent.currentState.availability || false;
            this.is_locked = parent.currentState.is_locked || false;
            this.state = parent.currentState.state || false;
            this.routing_id = parent.currentState.routing_id || false;
            this.check_to_done = parent.currentState.check_to_done || false;
            this.company_id = parent.currentState.company_id || false;
            this.all_wo_done = parent.currentState.all_wo_done || false;
        },
        start: function() {
            return this._super.apply(this, arguments);
        },
        _renderLines: function () {
            if (this.mode === "done") {
                if (this.model === "mrp.production") {
                    this._toggleScanMessage("production_already_done");
                } else {
                    return this._super();
                }
                return;
            } else if (this.mode === "cancel") {
                if (this.model === "mrp.production") {
                    this._toggleScanMessage("production_already_cancelled");
                } else {
                    return this._super();
                }
                return;
            }

            // Empty the header, render and reappend the pageSummary with the parent location data
            if (this.model === "stock.picking") {
                this._super();
                var $header = this.$el.filter(".o_barcode_lines_header");
                $header.empty();

                var $pageSummary = $(
                    QWeb.render("stock_barcode_summary_template", {
                        // Location
                        locationName: this.page.location_name,
                        // Location dest
                        locationDestName: this.page.location_dest_name,
                        // Parent
                        locationParent: this.page.location_parent,
                        locationParentFormat: this.page.location_parent_format,
                        // Gparent
                        locationGParent: this.page.location_gparent,
                        // Parent dest
                        locationDestParent: this.page.location_dest_parent,
                        locationDestParentFormat: this.page.location_dest_parent_format,
                        // Gparent dest
                        locationDestGParent: this.page.location_dest_gparent,
                        nbPages: this.nbPages,
                        pageIndex: this.pageIndex + 1,
                        mode: this.mode,
                        model: this.model,
                    })
                );
                $header.append($pageSummary);
                var $body = this.$el.filter('.o_barcode_lines');
                var $lines = $($body).find('.o_barcode_line');
                $lines.on('click', '.o_edit_split', this._onClickEditSplitLine.bind(this));
                $lines.on('click', '.o_edit_incoming_split', this._onClickEditSplitIncomingLine.bind(this));
            } else {
                return this._super();
            }
        },
        
        addProduct: function (lineDescription, model, doNotClearLineHighlight) {
            if (this.model === "stock.picking") {
                this._super.apply(this, arguments);
                var $body = this.$el.filter('.o_barcode_lines');
                var $lines = $($body).find('.o_barcode_line');
                $lines.on('click', '.o_edit_split', this._onClickEditSplitLine.bind(this));
                $lines.on('click', '.o_edit_incoming_split', this._onClickEditSplitIncomingLine.bind(this));
            } else {
                return this._super();
            }
        },

        incrementProduct: function (
            id_or_virtual_id,
            qty,
            model,
            doNotClearLineHighlight
        ) {
            if (model === "mrp.production") {
                var $line = this.$("[data-id='" + id_or_virtual_id + "']");
                var incrementClass = ".qty-done";
                var qtyDone = parseFloat($line.find(incrementClass).text());
                // Increment quantity and avoid insignificant digits
                $line
                    .find(incrementClass)
                    .text(parseFloat((qtyDone + qty).toPrecision(15)));
                this._highlightLine($line, doNotClearLineHighlight);

                this._handleControlButtons();

                if (qty === 0) {
                    this._toggleScanMessage("scan_lot");
                } else if (this.mode === "receipt") {
                    this._toggleScanMessage("scan_more_dest");
                } else if (["delivery", "inventory"].indexOf(this.mode) >= 0) {
                    this._toggleScanMessage("scan_more_src");
                } else if (this.mode === "internal") {
                    this._toggleScanMessage("scan_more_dest");
                } else if (this.mode === "no_multi_locations") {
                    this._toggleScanMessage("scan_products");
                }
            } else {
                return this._super();
            }
        },

        /**
         * Handles the click on the `edit button` on a line.
         *
         * @private
         * @param {jQuery.Event} ev
         */
        _onClickEditSplitLine: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var id = $(ev.target).parents('.o_barcode_line').data('id');
            this.ProductLineSplitModal = new ProductLineSplitModal(this).create(ev, id);
        },

        _onClickEditSplitIncomingLine: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var id = $(ev.target).parents('.o_barcode_line').data('id');
            this.ProducIncomingLineSplitModal = new ProductIncomingLineSplitModal(this).create(ev, id);
        },
        _onClickMarkAsDone: function (ev) {
            ev.stopPropagation();
            this.trigger_up("mark_as_done");
        },

        _onClickOkQuality: function (ev) {
            ev.stopPropagation();
            this.trigger_up("ok_quality");
        },

        _onClickButtonAssign: function (ev) {
            ev.stopPropagation();
            this.trigger_up("button_assign");
        },
    });
});
