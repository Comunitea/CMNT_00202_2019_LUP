odoo.define('custom_stock_barcode.ProductIncomingLineSplitModal', function(require) {
    'use strict';

    var core = require('web.core');
    var Widget = require('web.Widget');
    var ajax = require("web.ajax");

    var _t = core._t;

    var ProductIncomingLineSplitModal = Widget.extend({

        init: function(parent, parties, options) {
            this._super.apply(this, arguments);
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments)
        },

        create: function($targetEl, move_line_id) {
            var self = this;
            this.$currentTarget = $targetEl;
            var html = $(core.qweb.render('custom_stock_barcode.split_lines_popover', {move_line_id: move_line_id}));
            html.appendTo($('body'));
            html.modal('toggle');
            html.on('click', '.o_custom_stock_barcode_split_button', this._onClickButtonSplitLines.bind(this));
        },
        _onClickButtonSplitLines: function (ev) {
            var self = this;
            ev.preventDefault();
            var modal = $(ev.currentTarget).closest('div.modal');
            var product_uom_qty = modal.find('input[name="product_uom_qty"]').val();
            var move_line_id = modal.find('input[name="move_line_id"]').val();

            ajax.jsonRpc("/custom_stock_barcode/button_split_incoming_product_line", "call", {
                move_line_id: move_line_id,
                product_uom_qty: product_uom_qty,
            }).then(function (res) {
                if (res) {
                    modal.modal('toggle');
                    self.trigger_up("reload");
                }
            });
            
        }
    });

    return ProductIncomingLineSplitModal;
});