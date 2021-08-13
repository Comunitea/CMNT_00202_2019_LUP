# Copyright 2021 Comunitea - Kiko Sánchez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Change Currency purchases",
    "summary": "Change Purchase and Invoice Currency with custom rate",
    "version": "12.0.1.0.0",
    "author": "Comunitea",
    "category": "Inventory",
    "depends": ["account"],
    "data": ["wizard/change_invoice_currency_view.xml",
             "wizard/change_purchase_currency_view.xml",
             "views/account_invoice_view.xml",
             "views/purchase_order_view.xml"
             ],
    "installable": True,
    "license": "AGPL-3",
}
