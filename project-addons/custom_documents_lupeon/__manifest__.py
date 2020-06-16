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
    ],
    'data': [
        'views/report_sale.xml',
        'views/report_templates.xml',
    ],
    'installable': True,
}