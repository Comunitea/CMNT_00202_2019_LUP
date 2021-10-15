odoo.define('custom_stock_barcode.picking_client_action', function (require) {
    'use strict';

    var PickingClientAction = require('stock_barcode.picking_client_action');

    PickingClientAction.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
        },
        /**
         * @override
         */
        _getPageFields: function () {
            var res = this._super();
            res.push(
                // parent
                ['location_parent', 'location_id.location_id.display_name'],
                ['location_parent_format', 'location_id.location_id.loc_format'],
                // gparent
                ['location_gparent', 'location_id.location_id.location_id.display_name'],
                // parent dest
                ['location_dest_parent', 'location_dest_id.location_id.display_name'],
                ['location_dest_parent_format', 'location_dest_id.location_id.loc_format'],
                // gparent dest
                ['location_dest_gparent', 'location_dest_id.location_id.location_id.display_name'],
            )
            return res
        },      
    });

});