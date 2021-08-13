from odoo import api, fields, models, _

class StockRule(models.Model):
    _inherit = 'stock.rule'


    def _make_po_get_domain(self, values, partner):
        domain = super(StockRule, self)._make_po_get_domain(values, partner)
        # Busca una orden que sí tenga un origen definido
        domain += (('origin', '!=', ''),)
        return domain