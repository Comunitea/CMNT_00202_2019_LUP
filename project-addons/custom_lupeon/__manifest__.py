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
                "sale_margin", "sale_order_margin_percent", "stock_barcode",
                "stock", "account", "custom_prestashop", "l10n_es_facturae",
                "cost_sheet_lupeon","incident_manager", "mrp_bom_cost"],
    "data": [
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/invoice_view.xml',
        'views/stock_view.xml',
        'views/payment_mode_view.xml',
        'views/report_facturae.xml',
        'views/account_menus.xml',
        'views/product_view.xml'],
}
