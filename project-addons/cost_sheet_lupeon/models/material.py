# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

MATERIAL_TYPES = [
    ('fdm', 'FDM'),
    ('sls', 'SLS'),
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('dmls', 'DMLS'),
]

class Material(models.Model):

    _name = 'material'

    name = fields.Char('Name')
    type = fields.Selection(MATERIAL_TYPES, 'Tipo material')

    # FDM
    gr_cc = fields.Float('Gr/cc')
    euro_kg = fields.Float('€/kg')
    factor_hour = fields.Float('Factor hora')

    #SLS
    dens_cc = fields.Float('Densidad impreso gr/cc')
    dens_bulk = fields.Float('Densidad en bulk gr/cc')
    vel_cc = fields.Float('Velocidad cc/h full dense')
    vel_z = fields.Float('Velocidad en Z (cm/h) no exposur')
    euro_kg_bucket = fields.Float('€/kg cubeta')
    euro_hour_maq = fields.Float('€/H Maquina')