
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssignProdctionWzd(models.TransientModel):
    _name = 'assign.production.wzd'

    sale_id = fields.Many2one('sale.order', 'Asignar a')

    def confirm(self):
        productions = self.env['mrp.production'].browse(
            self._context.get('active_ids'))
        if productions:

            assigned = productions.filtered(
                lambda p: p.sale_line_id)
            if assigned:
                raise UserError('La producción ya está asociadada a una venta')

            productions.write({
                'sale_id': self.sale_id.id,
                'imprevist': True,
            })
        return
