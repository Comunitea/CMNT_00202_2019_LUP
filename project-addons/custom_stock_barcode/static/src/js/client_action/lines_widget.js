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
               // location
               locationName: this.page.location_name,
               // location dest
               locationDestName: this.page.location_dest_name,
               // parent
               locationParent: this.page.location_parent,
               locationParentFormat: this.page.location_parent_format,
               // gparent
               locationGParent: this.page.location_gparent,
               // parent dest
               locationDestParent: this.page.location_dest_parent,
               locationDestParentFormat: this.page.location_dest_parent_format,
               // gparent dest
               locationDestGParent: this.page.location_dest_gparent,
               nbPages: this.nbPages,
               pageIndex: this.pageIndex + 1,
               mode: this.mode,
               model: this.model,
           }));
           $header.append($pageSummary);
        }        
    });

});