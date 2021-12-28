# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Delivery custom Lupeon",
    "summary": "Add custom features to the delivery process",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "cmnt_delivery_carrier_label",
        "delivery_package_number",
        "base_delivery_carrier_label",
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
}
