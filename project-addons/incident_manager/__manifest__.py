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
        'views/res_partner.xml',
        'views/stock_picking.xml',
        'views/mrp_production.xml',
        'views/crm_lead.xml',
        'views/product_product.xml',
        'views/project_task.xml',
        'wizard/incident_report_wzd.xml',
        'data/incident_data.xml',
        'security/incident_security.xml'
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
}
