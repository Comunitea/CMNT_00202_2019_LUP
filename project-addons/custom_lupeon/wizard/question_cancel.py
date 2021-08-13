
from odoo import api, fields, models, _


class QuestionCancel(models.TransientModel):
    _name = 'question.cancel.wzd'

    def confirm(self):
        model = self._context.get('active_model')
        obj = self.env[model].browse(self._context.get('active_id'))
        obj.action_cancel()
