# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_incident_reports_count(self):
        for picking in self:
            incident_report_ids = self.env['incident.report'].search([
                ('res_id', '=', self.id),
                ('model_id', '=', self.env['ir.model'].search([('model', '=', self._name)]).id)
            ])
            picking.incident_reports_count = len(incident_report_ids)

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