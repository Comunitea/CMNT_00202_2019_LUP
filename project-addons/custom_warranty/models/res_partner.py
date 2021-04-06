# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.multi
    def open_partner_warranties(self):
        self.ensure_one()
        #domain = [('warranty_partner_id', 'in', self.child_ids.ids), ('under_warranty', '=', True)]
        all_partners = self.env['res.partner'].with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        action['domain'] = [('warranty_partner_id', 'in', all_partners.ids), ('under_warranty', '=', True)]
        action['view_id'] = self.env.ref('custom_warranty.view_serial_warranty').id
        action['views'][0] = (action['view_id'], 'tree')
        action['context'] = {'partner_id': self.id}
        return action


    @api.multi
    def _compute_partner_warranties(self):
        ## Copio sale order count. Si ellos lo hacen así, no soy yo quien de cambiarlo ....
        all_partners = self.env['res.partner'].with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])
        serial_order_groups = self.env['stock.production.lot'].read_group(
            domain=[('warranty_partner_id', 'in', all_partners.ids), ('under_warranty', '=', True)],
            fields=['warranty_partner_id'], groupby=['warranty_partner_id']
        )

        for group in serial_order_groups:
            partner = self.browse(group['warranty_partner_id'][0])
            while partner:
                if partner in all_partners:
                    partner.warranties_count += group['warranty_partner_id_count']
                partner = partner.parent_id

 
    warranties_count = fields.Integer('Warranties count', compute=_compute_partner_warranties)