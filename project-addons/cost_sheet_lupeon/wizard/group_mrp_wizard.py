
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GroupMrpWizard(models.TransientModel):
    _name = "group.mrp.wizard"
    _description = "Group MRP Wizard"

    name = fields.Char('Name')

    def do_group(self):
        production_ids =  self.env['mrp.production'].browse(
            self._context.get('active_ids', []))
        sheet_type_ref = production_ids[0].sheet_type
        printer_id_ref = production_ids[0].sheet_id.printer_id
        for mrp in production_ids:
            if mrp.sheet_type != sheet_type_ref:
                raise UserError(
                    _('No puedes agrupar distintos tipos de hojas'))
            if printer_id_ref and mrp.sheet_id.printer_id.id != printer_id_ref.id:
                raise UserError(
                    _('No puedes agrupar producciones con distinta categoría de impresora'))

        group = self.env['group.production'].create({
            'name': self.name,
            'sheet_type': sheet_type_ref,
            'printer_id': printer_id_ref.id
        })

        for prod in production_ids:
            wo = prod.workorder_ids.filtered(lambda x: x.active_move_line_ids)
            if not wo:
                raise UserError(
                    'No se encuentran consumos asociados a la orden de \
                    trabajo')
            vals = {
                'group_mrp_id': group.id,
                'workorder_id': wo.id,
                'qty_done': wo.qty_production,
            }
            self.env['group.register.line'].create(vals)

        view = self.env.ref(
            'cost_sheet_lupeon.group_production_view_form'
        )
        action = self.env.ref(
            'cost_sheet_lupeon.action_group_productions').read()[0]
        action['views'] = [(view.id, 'form')]
        action['res_id'] = group.id
        return action
