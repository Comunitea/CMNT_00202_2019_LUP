# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
#from odoo.exceptions import RedirectWarning, UserError, ValidationError



class HrEmployee(models.Model):

    _inherit = "hr.employee"

    file_ids = fields.One2many(comodel_name="hr.employee.file",
                               inverse_name='employee_id',
                                string="Files")
  
class HrEmployeeFile(models.Model):

    _name = "hr.employee.file"

    _order = 'date DESC'

    name = fields.Char(
        "Name", required=True
    )
    file_type_id = fields.Many2one(comodel_name="hr.file.type",
                                string='Type')
    datas = fields.Binary('File')
    date = fields.Date('Date', 
                        required=True,
                        default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee')


class HrFileType(models.Model):

    _name = "hr.file.type"
    
    name = fields.Char(
        "Name", required=True
    )

