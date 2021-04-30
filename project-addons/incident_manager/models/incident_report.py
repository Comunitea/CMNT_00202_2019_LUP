# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools, _

class ModelIncidentBase(models.AbstractModel):
    _name = "model.incident.base"
    _description = 'Model Incident'

    def _compute_incident_reports_count(self):
        for record in self:
            incident_report_ids = self.env['incident.report'].search([
                ('res_id', '=', self.id),
                ('model_id', '=', self.env['ir.model'].search([('model', '=', self._name)]).id)
            ])
            record.incident_reports_count = len(incident_report_ids)

    incident_reports_count = fields.Integer(
        compute='_compute_incident_reports_count',
    )

    @api.multi
    def action_incident_reports_view(self):
        action = self.env.ref('incident_manager.action_incident_report_form').read()[0]
        action['view_mode'] = 'tree'
        action['context'] = {
            'search_default_res_id': self.id,
            'search_default_model_id': self.env['ir.model'].search([('model', '=', self._name)]).id
        }
        return action

    def create_incident_report(self):
        # Redirect to wizard
        self.ensure_one()
        model_id = self.env['ir.model'].search([('model', '=', self._name)]).id
        if model_id:
            action = self.env.ref('incident_manager.action_create_incident_report_wzd_form').read()[0]
            action['view_mode'] = 'form'
            action['context'] = {
                'default_model_id': model_id,
                'default_res_id': self.id,
            }
            return action


class PrinterTechnolgy(models.Model):
    _name = "printer.technology"
    _description = "Printer Technology"

    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)



class IncidentProductionFail(models.Model):
    _name = "incident.production.fail"
    _description = "Incident Production Fail Type"

    technology_ids = fields.Many2many(
        comodel_name='printer.technology',
        string='Technology')
    name = fields.Char('Motivo',required=True)
    factor_type = fields.Selection(
        [('human', 'Humano'),
        ('machine', 'Máquina'),
        ('external', 'Externo')],
        required=False) 
    

class IncidentReportType(models.Model):
    _name = "incident.report.type"
    _description = "Incident Report Type"

    name = fields.Char()
    model_ids = fields.Many2many(
        comodel_name='ir.model',
        string='Documentos (modelos)',
    )
    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Tipo de albarán'
    )
    view_type = fields.Boolean("Ver tipo albarán", compute="_compute_view_type")

    @api.multi
    @api.depends('model_ids')
    def _compute_view_type(self):
        for record in self:
            picking_model = self.env['ir.model'].search([('model', '=', 'stock.picking')])
            if picking_model.id in record.model_ids.ids:       
                record.view_type = True
            else:
                record.view_type = False
        


class IncidentReport(models.Model):
    _name = "incident.report"
    _description = "Incident Report"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    
    name = fields.Text('Incident title')
    date = fields.Date('Date',
                       required=True,
                       default=fields.Date.context_today)
    incident_type = fields.Many2one(comodel_name='incident.report.type', string='Incident type')
    claimed_amount = fields.Float("Claimed Amount)")
    description = fields.Char('Description')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    model_id = fields.Many2one(
        'ir.model', string='Object'
    )
    res_id = fields.Integer(string='Record ID')
    state = fields.Selection([
        ('open', 'Abierta'),
        ('refund', 'Reembolso pendiente'),
        ('close', 'Cerrada')],
        default='open',
        required=True)
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier', compute='_get_origin_info', store=True, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', compute='_get_origin_info', store=True, readonly=True)
    product_id = fields.Many2one(comodel_name='product.product',
        string= 'Material',
        domain ="[('id', 'in', available_product_ids)]")
    available_product_ids = fields.Many2many(comodel_name='product.product',
        compute="compute_available_products")
    available_fails = fields.Many2many(comodel_name='incident.production.fail',
        compute="compute_available_fails")
    production_fail_id = fields.Many2one(comodel_name='incident.production.fail',
        string='Production Fail',
        domain ="[('id', 'in', available_fails)]"
        )
    carrier_tracking_ref = fields.Char('Tracking ref', compute='_get_origin_info', store=True, readonly=True )
    origin = fields.Char('Origin Document', compute='_get_origin_info', store=True, readonly=True)

    layer_height = fields.Float('Altura de Capa')
    perfil = fields.Char('Perfil')
    view_mrp_data = fields.Boolean('Mrp Data', compute="_compute_view_mrp_data", store=True)
    factor_type = fields.Selection(
        [('human', 'Humano'),
        ('machine', 'Máquina'),
        ('external', 'Externo')],
        required=False) 
    sheet_type = fields.Many2one(
        comodel_name='printer.technology',
        string='Technology')
    machine = fields.Char('Machine')
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute="_compute_company_id",
        required=False,
        string='Company',
        store=True
    )



    @api.depends('model_id', 'res_id')
    def _compute_company_id(self):
        for record in self:
            record.company_id = self.env[record.model_id.model].browse(record.res_id).company_id.id

    @api.onchange('production_fail_id')
    def onchange_production_fail_id(self):
        self.factor_type = self.production_fail_id.fail_id

    @api.depends('model_id', 'res_id')
    def _compute_view_mrp_data(self):
        for record in self:
            if record.model_id.model == 'mrp.production':
                record.view_mrp_data = True
            else:
                record.view_mrp_data = False

    @api.depends('model_id', 'res_id')
    def compute_available_products(self):
        for record in self:
            if record.model_id:
                if record.model_id.model != 'mrp.production':
                    record.available_products = False
                else:
                    if record.res_id:
                        product_ids = self.env['mrp.production'].browse(record.res_id).move_raw_ids.mapped('product_id')
                        if product_ids:
                            record.available_products = product_ids.ids
                        else:
                            record.available_products = False 


    @api.depends('model_id', 'res_id')
    def compute_available_fails(self):
        for record in self:
            if record.model_id:
                if record.model_id.model != 'mrp.production':
                    record.available_fails = False
                else:
                    if record.res_id:
                        sheet_type = self.env['mrp.production'].browse(record.res_id).sheet_type
                        technology_id = self.env['printer.technology'].search([('code', '=', sheet_type)])
                        if technology_id:
                            fails = self.env['incident.production.fail'].search([
                                ('technology_ids', 'in', technology_id.id)
                            ])
                            record.available_fails = fails.ids
                        else:
                            record.available_fails = False 


    @api.depends('model_id', 'res_id')
    def _get_origin_info(self):
        for incident in self:
            origin = self.env[incident.model_id.model].search([
                    ('id', '=', incident.res_id)
                ], limit=1)
            if origin:
                if 'carrier_id' in origin._fields:
                    if origin.carrier_id:
                        incident.carrier_id = origin.carrier_id.id
                    else:
                        incident.carrier_id = False  
                if 'carrier_tracking_ref' in origin._fields:
                    incident.carrier_tracking_ref = origin.carrier_tracking_ref
                if 'name' in origin._fields:
                    incident.origin = origin.name
                if 'partner_id' in origin._fields:
                    incident.partner_id = origin.partner_id.id

                if incident.model_id.model == 'mrp.production':
                    if origin.sheet_id:
                        technology_id = self.env['printer.technology'].search([('code', '=', origin.sheet_id.sheet_type)])
                        incident.sheet_type = technology_id.id
                        incident.layer_height = origin.sheet_id.layer_height
                        incident.perfil = origin.sheet_id.perfil
                        


        
    
    def open_origin_document(self):
        self.ensure_one()
        origin = self.env[self.model_id.model].search([
            ('id', '=', self.res_id)
        ], limit=1)
        if origin:
            return {
                'name': _('Origin document'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': self.model_id.model,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': origin.id,
            }
        else:
            raise UserError(_("There is no origin document for this incident report."))