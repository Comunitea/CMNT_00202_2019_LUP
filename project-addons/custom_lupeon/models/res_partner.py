# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


class ResPartner(models.Model):

    _inherit = "res.partner"

    admin_fact = fields.Float('Factor administrativo (%)')
    require_num_order = fields.Boolean('Requires num order')
    supplier_number = fields.Char('Supplier Number')
    valued_picking = fields.Boolean(
        default=False,)
    

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """Give preference to commercial names on name search, appending
        the rest of the results after. This has to be done this way, as
        Odoo overwrites name_search on res.partner in a non inheritable way."""
        if not args:
            args = []
        partners = self.search(
            [('vat', operator, name)] + args, limit=limit,
        )
        res = partners.name_get()
        if limit:
            limit_rest = limit - len(partners)
        else:  # pragma: no cover
            # limit can be 0 or None representing infinite
            limit_rest = limit
        if limit_rest or not limit:
            args += [('id', 'not in', partners.ids)]
            res += super(ResPartner, self).name_search(
                name, args=args, operator=operator, limit=limit_rest,
            )
        return res

    @api.multi
    def _get_admin_fact(self):
        if self.admin_fact:
            return self.admin_fact
        elif self.parent_id and self.parent_id.admin_fact:
            return self.parent_id.admin_fact
        else:
            return self.commercial_partner_id.admin_fact
        
    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = super()._get_name()
        print(name)
        if self._context.get('show_phone') :
            if partner.mobile or partner.phone:
                name = "%s \n %s  %s" % (name, partner.mobile or "", partner.phone or "")
        for cat in self.category_id:
            print(cat.name)
            if cat.name == 'Web F2P':
                name_arr = name.split('\n', 1)
                if len(name_arr) > 1:
                    name = "%s *\n%s" % (name_arr[0], name_arr[1])
                else:
                    name = "%s *" % (name)
        print(name)
        return name