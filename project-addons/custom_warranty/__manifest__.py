# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Serial Warranty',
    'version': '12.0.1.0.0',
    'summary': 'Warranty management on products. No RMA',
    'category': '',
    'author': 'Comunitea',
    'maintainer': 'Comunitea',
    'website': 'www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
    ],
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/product.xml',
        'views/stock_production_lot.xml',
        'views/res_partner.xml',
        'data/ir_config_parameter.xml',
    ],
}
