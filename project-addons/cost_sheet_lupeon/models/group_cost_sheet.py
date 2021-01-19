# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
import math
from datetime import datetime, timedelta


class GroupCostSheet(models.Model):

    _name = 'group.cost.sheet'
    _rec_name = 'sale_line_id'

    # display_name = fields.Char('Name', readonly="True")
    sale_line_id = fields.Many2one('sale.order.line', 'Línea de venta',
                                   readonly=False, copy=False)
    sale_id = fields.Many2one(
        'sale.order', 'Pedido de venta',
        related='sale_line_id.order_id', store=True, readonly=True)
    product_id = fields.Many2one(
        'product.product', 'Producto',
        related='sale_line_id.product_id')
    admin_fact = fields.Float(
        'Factor administrativo (%)',
        default=lambda self: self.env.user.company_id.admin_fact)

    ing_hours = fields.Integer(
        'Horas ingenieria',
        default=lambda self: self.env.user.company_id.ing_hours)
    tech_hours = fields.Integer(
        'Horas técnico',
        default=lambda self: self.env.user.company_id.tech_hours)
    help_hours = fields.Integer(
        'Horas ayudante',
        default=lambda self: self.env.user.company_id.help_hours)
    km_cost = fields.Float(
        'Coste Km',
        default=lambda self: self.env.user.company_id.km_cost
    )
    sheet_ids = fields.One2many(
        'cost.sheet', 'group_id', string='Cost Sheets', copy=True)
    line_pvp = fields.Float('PVP Línea', compute='_get_line_pvp')
    bom_id = fields.Many2one('mrp.bom', 'LdM', readonly=True,  copy=False)
    assembly_ids = fields.One2many(
        'assembly.cost.line', 'group_id', string='Assambley', copy=True)

    def name_get(self):
        res = []
        for sheet in self:
            res.append((sheet.id, ("[%s] %s") %
                       (sheet.sale_line_id.order_id.name,
                        sheet.sale_line_id.name)))
        return res

    def update_sale_line_price(self):
        for group in self:
            pu = group.line_pvp
            # Divido el precio entre el numero de unidades para obtener el
            # pvp unitario de verdad
            if group.sale_line_id.product_uom_qty:
                pu = group.line_pvp / group.sale_line_id.product_uom_qty

            if group.sale_id and group.sale_id.state in (
                    'draft', 'sent'):
                group.sale_line_id.write({'price_unit': pu})

    @api.depends('sheet_ids', 'assembly_ids')
    def _get_line_pvp(self):
        for group in self:
            line_pvp = 0
            line_pvp += sum([x.price_total for x in group.sheet_ids])
            line_pvp += sum([x.total for x in group.assembly_ids])
            group.line_pvp += line_pvp

    def create_group_components_on_fly(self, routing):
        """
        Obtengo los componentes de la lista de materiales que irá
        asociada al grupo de costes (por lo tanto a la línea de venta)
        """
        self.ensure_one()
        res = []
        mrp_types = ['fdm', 'sls', 'poly', 'sla', 'sls2', 'dmls']
        for sh in self.sheet_ids.filtered(
                lambda sh: sh.sheet_type in mrp_types):
            if not sh.product_id:
                print('error')
                continue

            operation_id = False
            if routing and routing.operation_ids:
                operation_id = routing.operation_ids[0].id
            vals = {
                'product_id': sh.product_id.id,
                'product_qty': sh.cus_units,  # TODO review,
                'product_uom_id': sh.product_id.uom_id.id,
                'operation_id': operation_id,
            }
            res.append((0, 0, vals))
        
        # Añadir compras como consumo
        for sh in self.sheet_ids.filtered(
                lambda sh: sh.sheet_type == 'purchase'):
            for line in sh.purchase_line_ids.filtered('product_id'):
                if line.product_id.type != 'product':
                    continue
                vals = {
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'product_uom_id': line.product_id.uom_id.id,
                    'operation_id': operation_id,
                }
                res.append((0,0, vals))
        return res

    def get_group_routing_on_fly(self):
        self.ensure_one()
        res = False
        if self.assembly_ids:
            values = []
            for assembly in self.assembly_ids:
                vals = {
                    'name': assembly.name or '/',
                    'workcenter_id': assembly.type.workcenter_id.id,
                }
                values.append((0, 0, vals))

            rout_vals = {
                'name': 'Ensamblaje:' + self.sale_id.name,
                'operation_ids': values,
                'created_on_fly': True,
                'active': False,
            }
            res = self.env['mrp.routing'].create(rout_vals)
        return res

    def create_group_bom_on_fly(self):
        """
        Creo la LdM asociada y la asocio al grupo de costes para poder luego
        pasarla en el values del método _prepare_procurement_values de la
        línea de venta, para que se me cree la producción bajo pedido con
        esta lísta de materiales.
        """
        bom = False
        for group in self:
            routing = group.get_group_routing_on_fly()
            line = group.sale_line_id
            components = group.create_group_components_on_fly(routing)
            vals = {
                'product_id': line.product_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'product_qty': line.product_uom_qty,
                'product_uom_id': line.product_uom.id,
                'routing_id': routing and routing.id or False,
                'type': 'normal',
                'bom_line_ids': components,
                'ready_to_produce': 'all_available',
                'created_on_fly': True
            }
            bom = self.env['mrp.bom'].create(vals)
            group.bom_id = bom.id
        return bom

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.update_sale_line_price()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.update_sale_line_price()
        return res


class AssemblyCostLine(models.Model):

    _name = 'assembly.cost.line'

    group_id = fields.Many2one('group.cost.sheet', 'Grupo de coste',
                               ondelete="cascade")

    name = fields.Char('Descripción', required=True)
    type = fields.Many2one('oppi.type', 'Tipo', required=True)
    time = fields.Float('Tiempo')
    total = fields.Float('PVP €', compute="_get_total")

    def _get_total(self):
        for line in self:
            line.total = line.time * line.group_id.tech_hours
