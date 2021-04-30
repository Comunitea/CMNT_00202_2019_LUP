# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom Warehouse",
    "version": "12.0.1.0.0",
    "category": "warehouse",
    "author": "Comunitea",
    "maintainer": "Comunitea",
    "website": "www.comunitea.com",
    "license": "AGPL-3",
    "depends": ["sale_stock", 
                "delivery",
                "stock_barcode",
                "stock", 
                "stock_move_location",
                "stock_removal_location_by_priority",
                "stock_putaway_product_form"],
    "qweb": [
    ],
    "data": [
        #'views/stock_move.xml',
        #'views/stock_picking.xml',
        #'views/product_view.xml',
        'views/stock_putaway.xml',
        'views/stock_location.xml',
    ],
}
