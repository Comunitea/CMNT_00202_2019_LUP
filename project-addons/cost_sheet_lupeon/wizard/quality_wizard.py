
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class QualityWizard(models.TransientModel):
    _name = "quality.wizard"

    @api.model
    def default_get(self, default_fields):
        """ Compute default partner_bank_id field for 'out_invoice' type,
        using the default values computed for the other fields.
        """
        res = super().default_get(default_fields)
        res['mode'] = self._context.get('mode')
        return res

    mode = fields.Selection(
        [('ok_tech', 'OK Tech'), ('ok_quality', 'OK Quality')], 'Mode',
         readonly=True)
    qty = fields.Integer('No OK Qty')

    def confirm(self):
        mrp =  self.env['mrp.production'].browse(
            self._context.get('active_ids', []))

        if self.qty > mrp.qty_produced:
             raise UserError(
            _('Cannot reject %s units because you only produce %s') %
            (self.qty, mrp.qty_produced))

        if self.mode == 'ok_tech':
            mrp.ok_tech = True
            mrp.no_ok_tech = self.qty
        else:
            mrp.ok_quality = True
            mrp.no_ok_quality = self.qty
        
        if self.qty > 0:
            mrp.create_partial_mrp(self.qty, self.mode)
        
        import ipdb; ipdb.set_trace()
        if self. mode == 'ok_quality':
            quants = self.env['stock.quant'].with_context(no_blocked=True).\
                _gather(mrp.product_id, mrp.location_dest_id)
            if quants:
                quants.sudo().write({'blocked': False})
