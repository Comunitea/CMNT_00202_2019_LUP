# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Custom Documents Lupeon',
    'version': '12.0.1.1.3',
    'summary': 'Reports Customization',
    'category': 'Document Management',
    'author': 'Coumnitea',
    'contributors': [
        'Javier Colmenero <javier@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'website': 'http://www.comunitea.com',
    "support": "info@comunitea.com",
    'license': 'AGPL-3',
    "price": 0,
    "currency": "EUR",
    'depends': [
        'account',
        'sale',
        'sale_stock',
        'stock',
        'cost_sheet_lupeon',
        'web',
        'custom_lupeon',
        'account_due_dates_str',
        'stock_picking_report_valued',
        'web_gantt',
        'sale_partner_incoterm',
        'sale_order_incoterm_place',
        'purchase',
        'purchase_stock',  # Have to replace Shipping address before
    ],
    'data': [
        'views/sale_view.xml',
        'views/invoice_view.xml',
        'views/custom_reports.xml',
        'views/report_purchase_order.xml',
        'views/report_purchase_quotation.xml',
        'views/report_sale.xml',
        'views/report_invoice.xml',
        'views/report_stock.xml',
        'views/report_templates.xml',
        'views/report_production_label.xml',
        'views/group_production_view.xml',
        'views/mrp_production_view.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}