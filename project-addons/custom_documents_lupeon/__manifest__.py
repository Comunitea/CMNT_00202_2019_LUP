# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Custom documents lupeon',
    'version': '12.0.1.0.0',
    'category': '',
    'author': 'Coumnitea',
    'license': 'AGPL-3',
    'license': '',
    'depends': [
        'account',
        'sale',
        'stock',
        'cost_sheet_lupeon',
        'web',
        'custom_lupeon',
        'account_due_dates_str',
        'stock_picking_report_valued',
        'web_gantt'
    ],
    'data': [
        'views/sale_view.xml',
        'views/invoice_view.xml',
        'views/custom_reports.xml',
        'views/report_sale.xml',
        'views/report_invoice.xml',
        'views/report_stock.xml',
        'views/report_templates.xml',
    ],
    'installable': True,
}