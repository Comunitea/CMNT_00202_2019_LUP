# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class SheetPerfil(models.Model):

    _name = 'sheet.perfil'
    _description = "Perfil"

    name = fields.Char('Name', required=True)
    printer_id = fields.Many2one(
        'printer.machine', 'Categoría impresora', required=True)
    infill = fields.Float('Infill')
    loops = fields.Integer('Loops')
    layer_height = fields.Float('Altura de Capa')

    material_ids = fields.Many2many(
        'product.template', 'product_perfil_rel',
        'perfil_id', 'material_id', 'Materiales',
        domain="[('is_material', '=', True)]"
    )
