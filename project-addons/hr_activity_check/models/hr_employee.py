# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import _, api, fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    min_report_hours = fields.Float(string="Hours to report", default=0.0)

    @api.model
    def cron_check_users_activity(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        if yesterday.weekday() > 4:
            return

        year_id = self.env["hr.holidays.public"].search(
            [
                ("year", "=", yesterday.year),
            ]
        )

        holiday = self.env["hr.holidays.public.line"].search(
            [
                ("year_id", "=", year_id.id),
                ("date", "=", yesterday),
            ]
        )

        if holiday:
            return

        users_to_check = self.env["hr.employee"].search(
            [
                ("min_report_hours", ">", 0.0),
            ]
        )

        for user in users_to_check.filtered(lambda x: x.is_absent_totay == False):
            yesterday_amount = 0.0
            reports = self.env["account.analytic.line"].search(
                [
                    ("employee_id", "=", user.id),
                    ("date", "=", yesterday),
                    ("unit_amount", ">", 0.0),
                ]
            )

            yesterday_amount = sum(report.unit_amount for report in reports)

            if yesterday_amount < user.min_report_hours:
                user.message_post(
                    body=_(
                        "The day {} you submitted {} hour/s of a total amount of {} hour/s.".format(
                            yesterday, yesterday_amount, user.min_report_hours
                        )
                    ),
                    message_type="email",
                    subtype="mail.mt_comment",
                )
