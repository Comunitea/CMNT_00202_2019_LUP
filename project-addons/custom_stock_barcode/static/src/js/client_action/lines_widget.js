odoo.define('custom_stock_barcode.LinesWidget', function (require) {
    'use strict';

    var core = require('web.core');
    var QWeb = core.qweb;
    var ClientAction = require('stock_barcode.LinesWidget');

    ClientAction.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
        },
        _renderLines: function () {
            this._super();
               
           // Empty the header, render and reappend the pageSummary with the parent location data
           var $header = this.$el.filter('.o_barcode_lines_header');
           $header.empty();

           var $pageSummary = $(QWeb.render('stock_barcode_summary_template', {
               locationName: this.page.location_name,
               locationPosx: this.page.location_posx,
               locationPosy: this.page.location_posy,
               locationPosz: this.page.location_posz,
               locationDestName: this.page.location_dest_name,
               locationDestPosx: this.page.location_dest_posx,
               locationDestPosy: this.page.location_dest_posy,
               locationDestPosz: this.page.location_dest_posz,
               locationParent: this.page.location_parent,
               locationDestParent: this.page.location_dest_parent,
               nbPages: this.nbPages,
               pageIndex: this.pageIndex + 1,
               mode: this.mode,
               model: this.model,
           }));
           $header.append($pageSummary);
        }        
    });

});