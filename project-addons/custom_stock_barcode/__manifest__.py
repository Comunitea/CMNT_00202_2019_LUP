# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom stock barcode",
    "version": "12.0.1.0.0",
    "category": "custom",
    "author": "Comunitea",
    "maintainer": "Comunitea",
    "website": "www.comunitea.com",
    "license": "AGPL-3",
    "depends": ["stock_barcode", "custom_warehouse"],
    "data": [
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/qweb_templates.xml",
    ],
    'installable': True,
}
