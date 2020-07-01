# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom Lupeon",
    "version": "12.0.1.0.0",
    "category": "connector",
    "author": "Comunitea",
    "maintainer": "Comunitea",
    "website": "www.comunitea.com",
    "license": "AGPL-3",
    "depends": ["product", "sale_stock", "delivery", "account_payment", 
                "sale_order_margin_percent", "stock_barcode"],
    "data": [
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/payment_mode_view.xml',
    ],
}
