# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class IncidentReportWiz(models.TransientModel):
    _name = 'incident.report.wzd'
    _description = "Incident Report Wizard"


    @api.multi
    def _compute_is_production(self):
       if self._context.get('default_model_id'):
            model_id = self.env['ir.model'].browse(self._context.get('default_model_id'))
            if model_id.model == 'mrp.production':
                return True
            else:
                return False


    @api.multi
    def compute_available_types(self):
        if self._context.get('default_model_id'):
            model_id = self.env['ir.model'].browse(self._context.get('default_model_id'))
            if model_id.model != 'stock.picking':
                types = self.env['incident.report.type'].search([('model_ids', 'in', model_id.id)])
                return types.ids
            else:
                if self._context.get('default_res_id'):
                    picking_type_id = self.env['stock.picking'].browse(self._context.get('default_res_id')).picking_type_id.id
                    types = self.env['incident.report.type'].search([
                        ('model_ids', 'in', model_id.id),
                        ('picking_type_id', '=', picking_type_id)
                    ])
                    return types.ids

    @api.multi
    def compute_available_fails(self):
        if self._context.get('default_model_id'):
            model_id = self.env['ir.model'].browse(self._context.get('default_model_id'))
            if model_id.model != 'mrp.production':
                return False
            else:
                if self._context.get('default_res_id'):
                    sheet_type = self.env['mrp.production'].browse(self._context.get('default_res_id')).sheet_type
                    technology_id = self.env['printer.technology'].search([('code', '=', sheet_type)])
                    if technology_id:
                        fails = self.env['incident.production.fail'].search([
                            ('technology_ids', 'in', technology_id.id)
                        ])
                        return fails.ids
                    else:
                        return False 


    @api.multi
    def compute_available_products(self):
        if self._context.get('default_model_id'):
            model_id = self.env['ir.model'].browse(self._context.get('default_model_id'))
            if model_id.model != 'mrp.production':
                return False
            else:
                if self._context.get('default_res_id'):
                    product_ids = self.env['mrp.production'].browse(self._context.get('default_res_id')).move_raw_ids.mapped('product_id')
                    if product_ids:
                        return product_ids.ids
                    else:
                        return False 




    name = fields.Char('Incident title', required=True)
    incident_type = fields.Many2one(comodel_name='incident.report.type',
        string='Incident type',
        required=True,
        domain ="[('id', 'in', available_types)]"
        )

    production_fail_id = fields.Many2one(comodel_name='incident.production.fail',
        string='Production Fail',
        required=False,
        domain ="[('id', 'in', available_fails)]"
        )
    model_id = fields.Many2one(
        'ir.model', string='Object', readonly=True
    )
    available_types = fields.Many2many(comodel_name='incident.report.type',
        default=compute_available_types)
    available_fails = fields.Many2many(comodel_name='incident.production.fail',
        default=compute_available_fails)
    product_id = fields.Many2one(comodel_name='product.product',
        string= 'Material',
        domain ="[('id', 'in', available_product_ids)]")
    available_product_ids = fields.Many2many(comodel_name='product.product',
        default=compute_available_products)
    res_id = fields.Integer(string='Record ID', readonly=True)
    date = fields.Date('Date',
                       required=True,
                       default=fields.Date.context_today)
    description = fields.Text('Description')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    is_production = fields.Boolean('Is Production?', default=_compute_is_production, readonly=True)


    def create_report(self):
        if self.model_id.model =='mrp.production':
            production = self.env['mrp.production'].browse(self.res_id)
            technology_id = self.env['printer.technology'].search([('code', '=', production.sheet_id.sheet_type)])
        else:
            technology_id = False
        report = self.env['incident.report'].create({
            'name': self.name,
            'incident_type': self.incident_type.id,
            'user_id': self.user_id and self.user_id.id or False,
            'date': self.date,
            'description': self.description,
            'model_id': self.model_id.id,
            'res_id': self.res_id,
            'product_id': self.product_id.id,
            'production_fail_id': self.production_fail_id.id,
            'sheet_type': technology_id and technology_id.id

        })

        return {
            'name': _('Incident Report'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'incident.report',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': report.id,
        }



    def create_report_and_close(self):
        if self.model_id.model =='mrp.production':
            production = self.env['mrp.production'].browse(self.res_id)
            technology_id = self.env['printer.technology'].search([('code', '=', production.sheet_id.sheet_type)])
        else:
            technology_id = False
        report = self.env['incident.report'].create({
            'name': self.name,
            'incident_type': self.incident_type.id,
            'user_id': self.user_id and self.user_id.id or False,
            'date': self.date,
            'description': self.description,
            'model_id': self.model_id.id,
            'res_id': self.res_id,
            'state': 'close',
            'product_id': self.product_id.id,
            'production_fail_id': self.production_fail_id.id,
            'sheet_type': technology_id and technology_id.id
        })

        return {
            'name': _('Incident Report'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'incident.report',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': report.id,
        }