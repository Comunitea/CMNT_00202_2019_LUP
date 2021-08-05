
from odoo import api, fields, models, _
from odoo.exceptions import UserError


SHEET_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS P396'),  # Renombrado
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('sls2', 'SLS'),  # Copia de sla, nuevo SLS
    ('dmls', 'DMLS'),
    ('unplanned', 'Imprevistos'),
    ('meets', 'Reuniones'),
    ('purchase', 'Compras'),
]


class AddGroupProductionWzd(models.TransientModel):
    _name = "add.group.production.wzd"
    _description = "Add Group Production Wizard"

    @api.model
    def default_get(self, default_fields):
        """ Compute default partner_bank_id field for 'out_invoice' type,
        using the default values computed for the other fields.
        """
        res = super().default_get(default_fields)
        group = self.env['group.production'].browse(
            self._context.get('active_ids', []))
        if not group.register_ids:
            return res
        sheet_type_ref = group.register_ids[0].production_id.sheet_type
        printer_id_ref = group.register_ids[0].production_id.sheet_id.printer_id
        res['sheet_type_ref'] = sheet_type_ref
        res['printer_id_ref'] = printer_id_ref
        return res

    sheet_type_ref = fields.Selection(SHEET_TYPES, 'Tipo de hoja')
    printer_id_ref = fields.Many2one('printer.machine', 'Categoría Impresora')
    production_ids = fields.Many2many('mrp.production')

    def confirm(self):
        group = self.env['group.production'].browse(
            self._context.get('active_ids', []))

        production_ids = self.production_ids
        # sheet_type_ref = group.register_ids[0].production_id.sheet_type
        sheet_type_ref = self.sheet_type_ref
        printer_id_ref = self.printer_id_ref

        for mrp in production_ids:
            if sheet_type_ref and mrp.sheet_type != sheet_type_ref:
                raise UserError(
                    _('No puedes agrupar distintos tipos de hojas'))
            if printer_id_ref and mrp.sheet_id.printer_id.id != printer_id_ref.id:
                raise UserError(
                    _('No puedes producciones con distinta categoría de impresora'))

        for prod in self.production_ids:
            wo = prod.workorder_ids.filtered(lambda x: x.active_move_line_ids)
            if not wo:
                wo = prod.workorder_ids.filtered(lambda x: x.state == 'done')
                if wo:
                    wo = wo[0]
            
            if not wo:
                raise UserError('No se encontro orden de trabajo de impresión')
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
        
