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

    name = fields.Text('Incident title')
    date = fields.Date('Date',
                       required=True,
                       default=fields.Date.context_today)
    incident_type = fields.Many2one(comodel_name='incident.report.type', string='Incident type')
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