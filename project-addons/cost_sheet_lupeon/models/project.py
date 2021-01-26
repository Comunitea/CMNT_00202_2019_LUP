# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class ProjectProject(models.Model):

    _inherit = "project.project"

    sale_id = fields.Many2one('sale.order', 'Sale Order', readonly=True)


class Projecttask(models.Model):

    _inherit = "project.task"

    sheet_id = fields.Many2one(
        'cost.sheet', 'Cost Sheet', readonly=True)
    oppi_line_id = fields.Many2one(
        'oppi.cost.line', 'Oppi Line', readonly=True)
    meet_line_id = fields.Many2one(
        'meet.cost.line', 'Meet Line', readonly=True)
    time_line_id = fields.Many2one(
        'design.time.line', 'Design Line', readonly=True)
    sale_id = fields.Many2one('sale.order', 'Sale Order',
                              related='sheet_id.sale_id', readonly=True,
                              store=True)
    show_planned_hours = fields.Boolean(string='Show planned Hours',
        compute='get_show_planned_hours',)


    @api.multi
    def get_show_planned_hours(self):
        """ Only display the planned hours 
         if the user has access to them """
        users = self.env.ref('base.group_no_one').users   #definir grupo
        for user in self:
            user.show_technical_features = user in users
