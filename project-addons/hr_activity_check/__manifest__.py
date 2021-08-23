# © 2021 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Activity Check",
    "summary": "",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_timesheet",
        "hr_holidays",
        "hr_holidays_public"
    ],
    "data": [
        "data/ir_cron.xml",
        "views/hr_employee.xml"
    ],
}
