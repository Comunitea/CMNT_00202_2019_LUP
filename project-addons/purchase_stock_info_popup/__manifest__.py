# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Extremely based on the module sale_stock_info_popup
# https://github.com/OCA/stock-logistics-warehouse/tree/12.0/sale_stock_info_popup
{
    "name": "Purchase Stock Info Popup",
    "summary": "Adds a popover in purchase order line to display "
    "stock info of the product",
    "author": "Comunitea",
    "website": "www.comunitea.com",
    "category": "Purchase",
    "version": "12.0.1.0.2",
    "license": "AGPL-3",
    "depends": [
        "custom_lupeon",
        "sale_stock_info_popup",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "qweb": [
        "static/src/xml/qty_at_date.xml",
    ],
    "installable": True,
}
