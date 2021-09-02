
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class QualityWizard(models.TransientModel):
    _name = "quality.wizard"
    _description = "Quality Wizard"

    @api.model
    def default_get(self, default_fields):
        """ 
        Get default ok tech ok quality.
        Por defecto sebería se siempre solo ok_tech, ya que no habrá ok_calidad
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

        auto_mode_done = False
        if self.mode == 'ok_tech':
            mrp.ok_tech = True
            mrp.message_post(body=_('OK Calidad'))
            mrp.no_ok_tech = self.qty
            # AUTO OK CALIDAD SI FABRICACIÓN HIJA Y NO HAY CANTIDAD NO OK
            # TODO definirlos en código??
            # if mrp.sheet_id and mrp.sheet_id.auto_ok_quality and not self.qty:
            #     mrp.ok_quality = True
            #     mrp.message_post(body=_('OK Calidad AUTO'))
            #     mrp.no_ok_quality = 0
            #     auto_mode_done = True
        else:
            mrp.ok_quality = True
            mrp.message_post(body=_('OK Calidad'))
            mrp.no_ok_quality = self.qty

        if self.qty > 0:
            mrp.create_partial_mrp(self.qty, self.mode)

        # if self.mode == 'ok_quality' or auto_mode_done:
        #     quants = self.env['stock.quant'].with_context(no_blocked=True).\
        #         _gather(mrp.product_id, mrp.location_dest_id)
        #     if quants:
        #         quants.sudo().write({'blocked': False})
        #         mrp.message_post(body=_('Stock desbloqueado'))
