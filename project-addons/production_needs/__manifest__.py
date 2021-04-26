# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Production needs Dativic",
    "summary": "View production needs for packs",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "mrp",
        "purchase_custom_lupeon"
    ],
    "data": [
        "views/product_views.xml",
        "wizard/product_production_wizard.xml",
    ],
}
