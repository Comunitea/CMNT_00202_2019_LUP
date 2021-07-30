# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    pline_description = fields.Char('Description')

    def _prepare_procurement_values(self):
        """
        Propagar LdM del grupo de costes a la producción.
        En Odoo el método _prepare_mo_vals de stock_rule (módulo mrp)
        Intenta obtener la LdM del método _get_matching_bom, el cual recibirá
        estos values
        """
        values = super()._prepare_procurement_values()
        line = self.sale_line_id
        if line and line.group_sheet_id and line.group_sheet_id.bom_id:
            values.update({
                'bom_id': line.group_sheet_id.bom_id,
                'line_ref': line.ref,
                'line_name': line.name,
            })
        return values


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(
        selection_add=[
            ('quality', 'Pendiente Calidad'),
        ])

    def action_quality(self):
        self.state = 'assigned'
        # self.action_confirm()


class StockLocation(models.Model):
    _inherit = 'stock.location'

    external_location = fields.Boolean('Ubicación externalización')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, values, bom):
        """
        """
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom)
        res.update({
            'line_ref': values.get('line_ref'),
            'line_name': values.get('line_name'),
        })
        return res