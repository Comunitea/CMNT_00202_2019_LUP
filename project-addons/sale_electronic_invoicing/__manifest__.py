# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Electronic Invoice Check",
    "summary": "Sale Electronic Invoice Check ",
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
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
        "views/res_config_settings_view.xml"
    ],
}
