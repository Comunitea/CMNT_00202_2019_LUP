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
               locationPosx: this.page.location_posx,
               locationPosy: this.page.location_posy,
               locationPosz: this.page.location_posz,
               // location dest
               locationDestName: this.page.location_dest_name,
               locationDestPosx: this.page.location_dest_posx,
               locationDestPosy: this.page.location_dest_posy,
               locationDestPosz: this.page.location_dest_posz,
               // parent
               locationParent: this.page.location_parent,
               locationParentFormat: this.page.location_parent_format,
               // gparent
               locationGParent: this.page.location_gparent,
               locationGParentPosx: this.page.location_gparent_posx,
               locationGParentPosy: this.page.location_gparent_posy,
               locationGParentPosz: this.page.location_gparent_posz,
               // parent dest
               locationDestParent: this.page.location_dest_parent,
               locationDestParentFormat: this.page.location_dest_parent_format,
               // gparent dest
               locationDestGParent: this.page.location_dest_gparent,
               locationDestGParentPosx: this.page.location_dest_gparent_posx,
               locationDestGParentPosy: this.page.location_dest_gparent_posy,
               locationDestGParentPosz: this.page.location_dest_gparent_posz,
               nbPages: this.nbPages,
               pageIndex: this.pageIndex + 1,
               mode: this.mode,
               model: this.model,
           }));
           $header.append($pageSummary);
        }        
    });

});