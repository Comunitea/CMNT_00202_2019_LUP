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