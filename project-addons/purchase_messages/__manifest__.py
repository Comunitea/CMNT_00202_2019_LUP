# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase messages ",
    "summary": "Messages related to pickings and/or invoices",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_messages",
        "purchase"
    ],
    "data": [
        "views/purchase_order_views.xml",
        "views/account_invoice_views.xml",
        "views/stock_picking_views.xml",
        #"security/ir.model.access.csv"
    ],
}
