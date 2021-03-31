# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Validate sale orders ",
    "summary": "Validate shipping address on sale orders before confirm ",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale"
    ],
    "data": [
        "views/sale_order_view.xml"
    ],
}
