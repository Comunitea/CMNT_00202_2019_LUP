# © 2022 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import  models, fields, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # General
    picking_with_return = fields.Boolean('With return', default=False)
    picking_insurance_value = fields.Float(digits=(4, 2), default=0.0)
    # GLS/ASM
    gls_asm_insurance_type = fields.Selection(
        selection=[('0', 'No'),
                   ('1', 'Normalized'),
                   ('2', 'Special moves')],
        string='GLS insurance type',
        default='0'
    )
    gls_asm_insurance_description = fields.Text('GLS insurance description')
    # SEUR
    seur_insurance_type = fields.Selection(
        selection=[('N', 'No'),
                   ('F', 'Comission on origin'),
                   ('D', 'Comision on destiny')],
        string='Seur insurance type',
        default='N'
    )

    def _get_cex_label_data(self):
        res = super()._get_cex_label_data()
        res['kilos'] = "%.3f" % (self.carrier_weight or 1)
        if self.picking_insurance_value and self.picking_insurance_value != 0.0:
            res['seguro'] = "{}".format(self.picking_insurance_value)
        if self.picking_with_return:
            res['producto'] = 54
        return res
