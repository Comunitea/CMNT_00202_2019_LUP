# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Incident Manager",
    "version": "12.0.1.0.0",
    "category": "custom",
    "author": "Comunitea",
    "maintainer": "Comunitea",
    "website": "www.comunitea.com",
    "license": "AGPL-3",
    "depends": ["purchase", "stock", "sale"],
    "data": [
        'security/ir.model.access.csv',
        'views/incident_views.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'wizard/incident_report_wzd.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
}
