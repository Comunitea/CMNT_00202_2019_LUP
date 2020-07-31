# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):

    _inherit = "res.company"

    check_commitment_date = fields.Boolean('Check commitmnent date')