# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class ProjectProject(models.Model):

    _inherit = "project.project"

    sale_id = fields.Many2one('sale.order', 'Sale Order', readonly=True)


class Projecttask(models.Model):

    _inherit = "project.task"

    sheet_id = fields.Many2one('cost.sheet', 'Cost Sheet', readonly=True)
    sale_id = fields.Many2one('sale.order', 'Sale Order',
                              related='sheet_id.sale_id', readonly=True, 
                              store=True)
