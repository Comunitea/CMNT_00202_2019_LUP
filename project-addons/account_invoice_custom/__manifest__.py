# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice Custom ',
    'summary': 'Customizations over Invoices',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'account',
        'account_payment_partner'
    ],
    'data': [
        'views/account_invoice.xml',
        'report/account_invoice_tax_report_view.xml',
        'security/ir.model.access.csv',
        'security/account_invoice_custom_security.xml'
    ]
}
