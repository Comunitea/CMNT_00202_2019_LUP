# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

class FarmTreatment(models.TransientModel):
    _name = 'incident.report.wzd'
    _description = "Incident Report Wizard"

    name = fields.Char('Incident title', required=True)
    incident_type = fields.Many2one(comodel_name='incident.report.type', string='Incident type', required=True)
    model_id = fields.Many2one(
        'ir.model', string='Object', readonly=True
    )
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

    def create_report(self):
        report = self.env['incident.report'].create({
            'name': self.name,
            'incident_type': self.incident_type.id,
            'user_id': self.user_id and self.user_id.id or False,
            'date': self.date,
            'description': self.description,
            'model_id': self.model_id.id,
            'res_id': self.res_id
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