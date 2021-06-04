# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

MATERIAL_TYPES = [
    ('fdm', 'FDM'),
    ('sls', 'SLS P396'),
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('sls2', 'SLS'),
    ('dmls', 'DMLS'),
]

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    cost_sheet_sale = fields.Boolean(related='company_id.cost_sheet_sale')
    is_material = fields.Boolean('Es un material')
    custom_mrp_ok = fields.Boolean('Fabricación lupeon')
    # material = fields.Boolean('Material')
    material_type = fields.Selection(MATERIAL_TYPES, 'Tipo material')

    # FDM
    gr_cc = fields.Float('Gr/cc')
    euro_kg = fields.Float('€/kg')
    factor_hour = fields.Float('Factor hora')
    diameter = fields.Float('Diametro')

    #SLS p396
    dens_cc = fields.Float('Densidad impreso gr/cc')
    dens_bulk = fields.Float('Densidad en bulk gr/cc')
    vel_cc = fields.Float('Velocidad cc/h full dense')
    vel_z = fields.Float('Velocidad en Z (cm/h) no exposur')
    euro_kg_bucket = fields.Float('€/kg cubeta')
    euro_hour_maq = fields.Float('€/H Maquina')

    # POLY
    # De momento uso el euro Kg
    
    # SLA
    euro_cc = fields.Float('€/cc')
    printer_id = fields.Many2one('printer.machine', 'Impresora')
    # washing_time = fields.Float('Tiempo Lavado')
    # cured_time = fields.Float('Tiempo curado')  # De momento uso el euro Kg

    # DMLS
    init_cost = fields.Float('Coste Inicial')
    term_cost = fields.Float('Coste ciclo tratamiento térmico')
    # dens_cc = fields.Float('Densidad impreso gr/cc')
    # euro_kg = fields.Float('€/kg')
    created_on_fly = fields.Boolean('Creado al vuelo')

    group_sheet_id = fields.Many2one(
        'group.cost.sheet', 'Grupo de costes reabastecimineto')

    perfil_ids = fields.Many2many(
        'sheet.perfil', 'product_perfil_rel',
        'material_id', 'perfil_id', 'Perfiles',
    )
