# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _


SHEET_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS P396'),
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('sls2', 'SLS'),
    ('dmls', 'DMLS'),
    ('unplanned', 'Imprevistos'),
    ('meets', 'Reuniones'),
    ('purchase', 'Compras'),
]


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    sheet_id = fields.Many2one('cost.sheet', 'Cost Sheet', readonly=True)
    sheet_type = fields.Selection(SHEET_TYPES, string='Sheet type',
                                  related='sheet_id.sheet_type', store=True)
    imprevist = fields.Boolean(
        'Fabricación imprevista', readonly=True)
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line',
                                   readonly=True)
    sale_id = fields.Many2one('sale.order', 'Sale Order',
                              related='sale_line_id.order_id', readonly=True,
                              store=True)
    line_ref = fields.Char('Referencia')
    line_name = fields.Char('Descripción')
    ok_tech = fields.Boolean('OK Calidad', copy=False, readonly=True)
    no_ok_tech = fields.Integer('Cant. NO OK', copy=False, readonly=True)
    ok_quality = fields.Boolean('OK quality 2', copy=False, readonly=True)
    no_ok_quality = fields.Integer(
        'Qty no ok quality 2', copy=False, readonly=True)
    repeated_production_ids = fields.One2many(
        'mrp.production', 'origin_production_id', 'Repeated production')
    origin_production_id = fields.Many2one(
        'mrp.production', 'Producción origen', readonly=True)

    qty_printed = fields.Float('Cant. impresa planificada',
                               compute='get_printed_qty')
    
    all_wo_done = fields.Boolean('All done', compute='_get_all_wo_done')

    @api.multi
    @api.depends('workorder_ids.state')
    def _get_all_wo_done(self):
        for production in self:
            wo_done = True
            if any([x.state not in ('done', 'cancel') for x in production.workorder_ids]):
                wo_done = False
            production.all_wo_done = wo_done
        return True

    # density = fields.Float('Density (%)')
    # bucket_height_sls = fields.Float('Altura cubeta (cm)')
    # dosaje_inf = fields.Float('Dosaje rango inferior (%) ')
    # dosaje_sup = fields.Float('Dosaje rango inferior (%) ')
    # dosaje_type = fields.Selection([
    #     ('sequencial', 'Sequencial'),
    #     ('permanent', 'Permanenete'),
    #     ('off', 'Off'),
    #     ], 'Tipo de dosaje')
    # desviation = fields.Float('Desviastion (%)')
    printer_instance_id = fields.Many2one('printer.machine.instance', 'Impresora')

    def _get_raw_move_data(self, bom_line, line_data):
        """
        Propagar la descripción de las líneas de compra
        """
        res = super()._get_raw_move_data(bom_line, line_data)
        if bom_line.pline_description:
            res.update(pline_description=bom_line.pline_description)
        return res


    def get_printed_qty(self):
        for prod in self:
            wo = prod.workorder_ids.filtered(lambda x: x.active_move_line_ids)
            if not wo:
                wo = prod.workorder_ids.filtered(lambda x: x.state == 'done')
                if wo:
                    wo = wo[0]
            if wo:
                domain = [
                    ('workorder_id', '=', wo.id),
                ]
                lines = self.env['group.register.line'].search(domain)
                if lines:
                    prod.qty_printed = sum(
                        [x.qty_done for x in lines if x.group_mrp_id.state in ['planned', 'progress', 'done']])

    #  TODO FECHA
    def create_partial_mrp(self, qty, mode):
        """
        When OK tech or OK quality, replan a production
        """
        self.ensure_one()
        version = len(self.repeated_production_ids) + 1
        mrp = self.copy({
            'name': self.name + ' - R%s' % version,
            # 'product_uom_qty': qty,
            'sheet_id': self.sheet_id.id,
            'origin_production_id': self.id,
        })

        # Por algun motivo no se duplica con lo que yo le digo
        # mrp.write({'product_uom_qty': qty})

        # Change the quantity of the production order to qty
        wiz = self.env['change.production.qty'].create(
            {'mo_id': mrp.id, 'product_qty': qty})
        wiz.change_prod_qty()

        mrp.button_plan()

    @api.multi
    @api.depends('workorder_ids.state', 'move_finished_ids', 'is_locked')
    def _get_produced_qty(self):
        res = super()._get_produced_qty()
        for production in self:
            # Solo en compañía lupeon, davitic deberia tener este check a True
            # y lupeon a false
            if not production.company_id.cost_sheet_sale:
                # production.qty_produced = production.qty_produced - \
                #     production.no_ok_tech - production.no_ok_quality
                production.qty_produced = production.qty_produced - \
                    production.no_ok_tech

            # Si no tiene grupo de finalizar produción (viejo ok quality)
            # tampoco tiene el auto_ok_qualyty, que ahora es permitir finalizar
            #  No mostrar botón de finalizar 
            if not self.user_has_groups('cost_sheet_lupeon.group_ok_quality') \
                    and not production.sheet_id or (production.sheet_id
                    and not production.sheet_id.auto_ok_quality):
                production.check_to_done = False        
        return res

    # def block_stock(self):
    #     self.ensure_one()
    #     quants = self.env['stock.quant']._gather(
    #         self.product_id, self.location_dest_id)
    #     if quants:
    #         quants.sudo().write({'blocked': True})

    @api.multi
    def button_mark_done(self):
        res = super().button_mark_done()
        # Solo en compañía lupeon, davitic deberia tener este check a True
        # y lupeon a false
        if not self.company_id.cost_sheet_sale:
            # self.block_stock()
            # CREAR SCRAP (No necesario al mover este momento antes de done)
            if self.no_ok_tech:
                vals = {
                    'product_id': self.product_id.id,
                    'product_uom_qty': self.no_ok_tech,
                    'scrap_qty': self.no_ok_tech,
                    'product_uom_id': self.product_uom_id.id,
                    'production_id': self.id,
                    'origin': self.name + ' (%s)' % 'OK calidad'
                }
                scrap = self.env['stock.scrap'].with_context(
                    no_blocked=True, ok_check=True).create(vals)
                scrap.action_validate()
        return res
