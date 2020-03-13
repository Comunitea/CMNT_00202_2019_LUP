# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cost Sheet Lupeon',
    'version': '12.0.0.0',
    'author': 'Custom ',
    "category": "Sales",
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'contributors': [
        "Comunitea ",
        "Javier Colmenero <javier@comunitea.com>"
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/cost_sheet_view.xml',
        'views/sale_view.xml',
    ],
    "installable": True,
    'application': False,
}
