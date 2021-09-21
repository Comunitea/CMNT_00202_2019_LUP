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
                ['location_parent_posx', 'location_id.location_id.posx'],
                ['location_parent_posy', 'location_id.location_id.posy'],
                ['location_parent_posz', 'location_id.location_id.posz'],
                // gparent
                ['location_gparent', 'location_id.location_id.location_id.display_name'],
                ['location_gparent_posx', 'location_id.location_id.location_id.posx'],
                ['location_gparent_posy', 'location_id.location_id.location_id.posy'],
                ['location_gparent_posz', 'location_id.location_id.location_id.posz'],
                // parent dest
                ['location_dest_parent', 'location_dest_id.location_id.display_name'],
                ['location_dest_parent_format', 'location_dest_id.location_id.loc_format'],
                ['location_dest_parent_posx', 'location_dest_id.location_id.posx'],
                ['location_dest_parent_posy', 'location_dest_id.location_id.posy'],
                ['location_dest_parent_posz', 'location_dest_id.location_id.posz'],
                // gparent dest
                ['location_dest_gparent', 'location_dest_id.location_id.location_id.display_name'],
                ['location_dest_gparent_posx', 'location_dest_id.location_id.location_id.posx'],
                ['location_dest_gparent_posy', 'location_dest_id.location_id.location_id.posy'],
                ['location_dest_gparent_posz', 'location_dest_id.location_id.location_id.posz'],
                // location
                ['location_posx', 'location_id.posx'],
                ['location_posy', 'location_id.posy'],
                ['location_posz', 'location_id.posz'],
                // location dest
                ['location_dest_posx', 'location_dest_id.posx'],
                ['location_dest_posy', 'location_dest_id.posy'],
                ['location_dest_posz', 'location_dest_id.posz'],
            )
            return res
        },      
    });

});