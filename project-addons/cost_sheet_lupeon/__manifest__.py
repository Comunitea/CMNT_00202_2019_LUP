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
        'stock_picking_report_valued',
        'project',
        'mrp',
        'hr',
        'purchase',
        'mrp_workorder',
    ],
    'contributors': [
        "Comunitea ",
        "Javier Colmenero <javier@comunitea.com>"
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/sheet_security.xml',
        'wizard/quality_wizard_view.xml',
        'wizard/group_mrp_wizard_view.xml',
        'wizard/register_workorder_view.xml',
        'data/sheet_data.xml',
        'data/stock_data.xml',
        'views/sale_view.xml',
        'views/stock_location_view.xml',
        'views/cost_sheet_view.xml',
        'views/applicable_legislation_view.xml',
        'views/part_feature_view.xml',
        'views/oppi_type_view.xml',
        'views/printer_machine.xml',
        'views/product_view.xml',
        'views/design_software_view.xml',
        'views/project_view.xml',
        'views/mrp_production_view.xml',
        'views/group_production_view.xml',
        'views/mrp_workorder_views.xml',
        'views/res_company_view.xml',
    ],
    "installable": True,
    'application': False,
}
