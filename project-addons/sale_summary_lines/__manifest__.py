# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Summary lines in sale orders ",
    "summary": "Summary Lines in sale orders ",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
        "delivery"
    ],
    "data": [
        "views/sale_order_view.xml",
        "security/ir.model.access.csv"
    ],
}
