# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api

class ProductTemplate(models.Model):

    _inherit = "product.template"

    list_price = fields.Float(
        default=0.0,
        )


class ProductProduct(models.Model):

    _inherit = "product.product"

    pop_up_info_date = fields.Char('Info date', compute='_compute_info_date')

    def generate_auto_ean(self):
        self.ensure_one()
        if not self.barcode:
            autoean = self.env['ir.sequence'].next_by_code('auto.ean')
            self.barcode = autoean

    def _compute_info_date(self):
        for p in self:
            date_str = ''
            domain = [
                ('product_id', '=', p.id),
                ('state', 'in', ['confirmed', 'assigned']),
                ('picking_code', '=', 'incoming'),
            ]
            moves = self.env['stock.move'].search(domain, order="id")
            if moves:
                dates_list = moves.mapped('date_expected')
                for d in dates_list:
                    str_date = d.strftime('%d-%m-%Y')
                    date_str +=  str_date + ',\n'
            p.pop_up_info_date = date_str

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        Buscar en nombres de proveedor y en código de barras.
        """
        if not args:
            args = []
        my_domain = []
        res2 = []
        res = super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

        # Aunque por barcode ya se busca, no se hace caracter a caracter
        # Añado pues la busqueda
        if name and operator in ["=", "ilike", "=ilike", "like", "=like"]:
            my_domain = args + [
                '|', '|',
                ("seller_ids.product_name", operator, name),
                ("seller_ids.product_code", operator, name),
                ("barcode", operator, name),
            ]
        if my_domain:
            products = self.search(my_domain)
            res2 = products.name_get()
        if res2:
            res.extend(res2)
        return res