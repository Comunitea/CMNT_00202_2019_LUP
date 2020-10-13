
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GroupMrpWizard(models.TransientModel):
    _name = "group.mrp.wizard"

    name = fields.Char('Name')

    def do_group(self):
        production_ids =  self.env['mrp.production'].browse(
            self._context.get('active_ids', []))
        sheet_type_ref = production_ids[0].sheet_type
        for mrp in production_ids:
            if mrp.sheet_type != sheet_type_ref:
                raise UserError(
                    _('No puedes agrupar distintos tipos de hojas'))

            # if mrp.group_mrp_id:
            #     raise UserError(
            #         _('Production %s already in a group') % mrp.name)

            # if mrp.state != 'planned':
            #     raise UserError(
            #         _('Production %s must be planned without nothing done')
            #         % mrp.name)

        group = self.env['group.production'].create({
            'name': self.name
        })
        
        # production_ids.write({'group_mrp_id': group.id})
        for prod in production_ids:
            wo = prod.workorder_ids.filtered(lambda x: x.active_move_line_ids)
            vals = {
                'group_mrp_id': group.id,
                'workorder_id': wo.id,
                # 'production_id': wo.production_id.id,
                # 'product_id': wo.product_id.id,
                # 'product_qty': wo.qty_production,
                # 'qty_produced': wo.qty_produced,
                # 'qty_done': wo.planned_qty if wo.planned_qty else
                'qty_done':0,
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
