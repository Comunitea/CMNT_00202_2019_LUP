# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Validate partners ",
    "summary": "Validate partneer before confirm Sale Orders",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "website": "comunitea.com",
    "author": "Comunitea",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale"
    ],
    "data": [
        "security/groups.xml",
        "views/res_partner_views.xml",
        
    ],
}
