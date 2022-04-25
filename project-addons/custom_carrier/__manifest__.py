# Copyright 2022 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Carrier Custom (SEUR/GLS/FEDEX)",
    "version": "12.0.0.0.0",
    "category": "Delivery",
    "license": "AGPL-3",
    "summary": "Customize delivery carrier integration",
    "author": "Comunitea",
    "website": "http://www.comunitea.com",
    "depends": ["delivery_seur", "delivery_gls_asm", "delivery_fedex"],
    "data": [
        "views/delivery_view.xml",
    ],
    "installable": True,
}
