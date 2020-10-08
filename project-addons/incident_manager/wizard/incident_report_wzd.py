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

    def create_report(self):
        report = self.env['incident.report'].create({
            'name': self.name,
            'incident_type': self.incident_type.id,
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