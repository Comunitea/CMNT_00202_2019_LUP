# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools, _

class IncidentReportType(models.Model):
    _name = "incident.report.type"
    _description = "Incident Report Type"

    name = fields.Char()

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
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier', compute='_get_origin_info')
    carrier_tracking_ref = fields.Char('Tracking ref', compute='_get_origin_info' )
    origin = fields.Char('Origin Document', compute='_get_origin_info')
    
    
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