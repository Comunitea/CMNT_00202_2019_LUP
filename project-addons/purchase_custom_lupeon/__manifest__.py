# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase custom Lupeon",
    "summary": "Add custom features to the Product model for help in Purchase Process",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "purchase"
    ],
    "data": [
        #"views/res_partner_views.xml",
        "views/purchase_order_views.xml",
        "views/product_views.xml",
        #"views/sale_order_views.xml",
        #"views/stock_view.xml",
        #"security/ir.model.access.csv",
        #"wizard/purchase_line_change_supplier_wzd.xml",
        #"wizard/purchase_order_line_confirm_changes.xml",
        "data/ir_cron.xml",
    ],
}
