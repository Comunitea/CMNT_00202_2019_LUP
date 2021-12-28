# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom stock barcode",
    "version": "12.0.1.0.0",
    "category": "custom",
    "author": "Comunitea",
    "maintainer": "Comunitea",
    "website": "www.comunitea.com",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "stock_barcode",
        "custom_warehouse",
        "mrp",
        "custom_documents_lupeon",
        "incident_manager",
    ],
    "data": [
        "data/data.xml",
        "views/stock_picking_views.xml",
        "views/mrp_production_views.xml",
        "views/assets.xml",
        "wizard/mrp_production_move_wzd.xml",
    ],
    "qweb": [
        "static/src/xml/qweb_templates.xml",
        "static/src/xml/stock_barcode.xml",
    ],
    "installable": True,
}
