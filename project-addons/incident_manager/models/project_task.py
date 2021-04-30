# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = ["project.task", "model.incident.base"]
    _name = "project.task"

