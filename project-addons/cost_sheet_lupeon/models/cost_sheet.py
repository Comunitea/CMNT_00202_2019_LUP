# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
import math
from datetime import datetime, timedelta


SHEET_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS P396'),  # Renombrado
    ('poly', 'Poly'),
    ('sla', 'SLA'),
    ('sls2', 'SLS'),  # Copia de sla, nuevo SLS
    ('dmls', 'DMLS'),
    ('unplanned', 'Imprevistos'),
    ('meets', 'Reuniones'),
    ('purchase', 'Compras'),
]


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
    admin_fact = fields.Float('Factor administrativo (%)')

    ing_hours = fields.Integer('Horas ingenieria', default=55)
    tech_hours = fields.Integer('Horas técnico', default=35)
    help_hours = fields.Integer('Horas ayudante', default=35)
    km_cost = fields.Float('Coste Km', default=0.30)
    sheet_ids = fields.One2many(
        'cost.sheet', 'group_id', string='Cost Sheets', copy=True)
    line_pvp = fields.Float('PVP Línea', compute='_get_line_pvp')
    bom_id = fields.Many2one('mrp.bom', 'LdM', readonly=True,  copy=False)

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

    @api.depends('sheet_ids')
    def _get_line_pvp(self):
        for group in self:
            group.line_pvp = sum([x.price_total for x in group.sheet_ids])

    def create_components_on_fly(self):
        """
        Obtengo los componentes de la lista de materiales que irá
        asociada al grupo de costes (por lo tanto a la línea de venta)
        """
        self.ensure_one()
        res = []
        mrp_types = ['fdm','sls', 'poly', 'sla', 'sls2', 'dmls']
        for sh in self.sheet_ids.filtered(
                lambda sh: sh.sheet_type in mrp_types):
            if not sh.product_id:
                print('error')
                continue
            vals = {
                'product_id': sh.product_id.id,
                'product_qty': sh.cus_units,  # TODO review,
                'product_uom_id': sh.product_id.uom_id.id,
                'operation_id': False,
            }
            res.append((0,0, vals))
        return res

    def create_bom_on_fly(self):
        """
        Creo la LdM asociada y la asocio al grupo de costes para poder luego
        pasarla en el values del método _prepare_procurement_values de la
        línea de venta, para que se me cree la producción bajo pedido con
        esta lísta de materiales.
        """
        bom = False
        for group in self:
            line = group.sale_line_id
            components = group.create_components_on_fly()
            vals = {
                'product_id': line.product_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'product_qty': line.product_uom_qty,
                'product_uom_id': line.product_uom.id,
                'routing_id': False,  # esta no lleva ruta,
                'type': 'normal',
                'bom_line_ids': components,
                'ready_to_produce': 'all_available',
            }
            bom = self.env['mrp.bom'].create(vals)
            group.bom_id = bom.id

        return bom


class CostSheet(models.Model):

    _name = 'cost.sheet'

    # COMUN
    name = fields.Char('Referencia', required=True)
    product_id = fields.Many2one(
        'product.product', 'Producto asociado', readonly=True)
    group_id = fields.Many2one(
        'group.cost.sheet', 'Hojas de coste', ondelete="cascade",
        readonly=True, copy=False)
    production_id = fields.Many2one(
        'mrp.production', 'Produción', index=True, copy=False,
        readonly=True)
    production_state = fields.Selection(
        string="Production State", related='production_id.state')
    sale_state = fields.Selection(
        string="Sale State", related='sale_id.state')

    sheet_type = fields.Selection(SHEET_TYPES, 'Tipo de hoja')

    sale_line_id = fields.Many2one(
        'sale.order.line', 'Línea de venta',
        related='group_id.sale_line_id', store=True, readonly=True)
    sale_id = fields.Many2one(
        'sale.order', 'Pedido de venta',
        related='group_id.sale_line_id.order_id', store=True, readonly=True)

    cost_init = fields.Float('Coste inicial')
    cost_init_computed = fields.Float(
        'Coste inicial', compute='_get_cost_prices')
    cost_ud = fields.Float('Coste', compute="_get_cost_prices")
    admin_fact = fields.Float(
        'Factor administrativo (%)', related='group_id.admin_fact')
    disc_qty = fields.Float('Descuento cantidad (%)')
    disc_qty_computed = fields.Float(
        'Descuento cantidad (%)', compute='_get_cost_prices')
    use_disc_qty = fields.Boolean('Usar descuento cantidad', default=True)
    disc2 = fields.Float('Descuento adicional (%)')
    increment = fields.Float('Incremento no estándar (%)')
    inspection_type = fields.Selection(
        [('visual', 'Visual'), ('tech', 'Técnica')],
        string="Tipo de inspeción", default="visual")
    price_unit = fields.Float('PVP unidad', compute='_get_cost_prices')
    price_total = fields.Float('PVP TOTAL', compute='_get_cost_prices')


    # DATOS PIEZA
    cus_units = fields.Integer('Uds. Cliente')
    cc_ud = fields.Float('cc ud')
    euros_cc = fields.Float('€/cc', compute='get_euros_cc_fdm')

    printer_id = fields.Many2one('printer.machine', 'Impresora')

    # [ALL] COSTE MANO DE OBRA
    workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sheet_id', string='Coste Mano de obra',
        copy=True)
    workforce_total_euro_ud = fields.Float(
        'Total € ud', compute="_get_totals_workforce")
    workforce_total = fields.Float(
    'Total', compute="_get_totals_workforce")

    # [ALL] COSTE EXTERNALIZACION POR PIEZA
    outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'sheet_id',
        string='Coste externalizacion por pieza', copy=True)
    outsorcing_total_ud = fields.Float(
        'Total ud', compute="_get_totals_outsorcing")
    outsorcing_total = fields.Float(
    'Total', compute="_get_totals_outsorcing")

    #PROPIOS DE DISEÑO
    flat_ref = fields.Char('Plano')
    legislation_ids = fields.Many2many(
        'applicable.legislation',
        'cost_sheet_applicable_legislation_rel',
        'sheet_id', 'legislation_id',
        string='Legislación aplicable')
    time_line_ids = fields.One2many(
        'design.time.line', 'sheet_id', string='Tiempos', copy=True)
    description = fields.Text('Requisitos técnicos')
    customer_note = fields.Text('Comentarios Cliente')
    hours_total = fields.Float('Horas totales', compute="_get_totals_design")
    amount_total = fields.Float('Importe TOTAL', compute="_get_totals_design")

    # FDM PARÁMETROS IMPRESIÓN

    tray_units = fields.Integer('Uds. Bandeja')
    infill = fields.Float('Infill')  # Model or selection?
    loops = fields.Integer('Loops') # Model or selection?
    layer_height = fields.Float('Altura de Capa') # Model or selection?
    tray_hours = fields.Float('h Maq. Bandeja')
    euro_machine = fields.Float('€/h maq',  compute='get_euro_machine')
    perfil = fields.Char('Perfil')

    # FDM COSTE MATERIAL
    material_cost_ids = fields.One2many(
        'material.cost.line', 'sheet_id', string='Coste material', copy=True)
    total_euro_ud = fields.Float(
        'Total € ud', compute='_get_totals_material_cost')
    total_material_cost = fields.Float(
        'Total', compute='_get_totals_material_cost')
    # COSTE MÁQUINA
    machine_hours = fields.Float(
        'Horas Maq total', compute='_get_fdm_machine_cost')
    euro_machine_ud = fields.Float(
        'Euros Maq ud', compute='_get_fdm_machine_cost')
    euro_machine_total = fields.Float(
        'Euros Maq total', compute='_get_fdm_machine_cost')
    # FDM PART FEATURES
    feature_ids = fields.Many2many(
        'part.feature',
        'cost_sheet_paer_features_rel',
        'sheet_id', 'feature_id',
        string='Características pieza')

    # ------------------------------------------------------------------------

    # SLS DATOS PIEZA
    cus_units = fields.Integer('Uds. Cliente')

    cm2_sls = fields.Float('cm^2 ud')
    x_mm_sls = fields.Float('X (mm)')
    y_mm_sls = fields.Float('Y (mm)')
    z_mm_sls = fields.Float('Z (mm)')
    e_cc_sls = fields.Float('€/cc', compute="_get_e_cc_sls")

    # SLS PARÁMETROS IMPRESIÓN
    print_increment = fields.Float('Incremento (mm)', default=18.0)
    tray_hours_sls = fields.Float(
        'h Maq. Bandeja', compute='_get_sls_print_totals', digits=(16, 3))


    # SLS OFERT CONFIGURATION
    offer_type = fields.Selection(
        [('standard', 'Standard'),
         ('xyz', 'XYZ'),
         ('cubeta', 'Cubeta')], 'Tipo oferta', default='standard')
    solid_per_sls = fields.Float('% Solido', default=80.0)
    bucket_height_sls = fields.Float('Altura cubeta')
    simulation_time_sls = fields.Float('Tiempo impresión simulacion')


    # SLS COSTE EXTERNALIZACION POR PIEZA
    tinted_id = fields.Many2one('tinted', 'Tintado')


    # POLY PARÁMETROS IMPRESIÓN
    finish_pol = fields.Selection([
        ('glossy', 'Glossy'),
        ('mate', 'Mate')], 'Acabado')

    # DMLS DATOS PIEZA
    units_dmls = fields.Integer('Uds. Cliente')
    use_treatment = fields.Boolean('Usar tratamiento térmico')
    heat_treatment_cost = fields.Float(
        'Tratamiento térmico', compute='_get_heat_treatment_cost')

    cc_soport_dmls = fields.Float('cc soporte')

    # Unplaned cost
    unplanned_cost = fields.Float('Coste Imprevisto')

    # REUNIONES
    meet_line_ids = fields.One2many(
        'meet.cost.line', 'sheet_id', string='Coste reuniones', copy=True)
    meet_hours_total = fields.Float('Horas totales', compute="_get_totals_meet")
    meet_total = fields.Float('TOTAL', compute="_get_totals_meet")

    # COMPRAS
    purchase_line_ids = fields.One2many(
        'purchase.cost.line', 'sheet_id', string='Coste reuniones', copy=True)
    purchase_total = fields.Float('TOTAL', compute="_get_totals_purchase")

    # OPPI
    oppi_line_ids = fields.One2many(
        'oppi.cost.line', 'sheet_id', string='Oppi', copy=True)
    total_oppi = fields.Float('Time Total', compute="_get_oppi_total")

    can_edit = fields.Boolean(compute='_compute_can_edit')

    def _compute_can_edit(self):
        for sh in self:
            sh.can_edit = sh.env.user.has_group(
                'cost_sheet_lupeon.group_cs_advanced') or \
                    sh.env.user.has_group(
                        'cost_sheet_lupeon.group_cs_manager')


    @api.depends('oppi_line_ids')
    def _get_oppi_total(self):
        for sh in self:
            sh.total_oppi = sum([x.time for x in sh.oppi_line_ids])

    @api.depends('meet_line_ids')
    def _get_totals_meet(self):
        for sh in self:
            sh.meet_hours_total = sum([x.hours for x in sh.meet_line_ids])
            sh.meet_total = sum([x.pvp for x in sh.meet_line_ids])

    @api.depends('purchase_line_ids')
    def _get_totals_purchase(self):
        for sh in self:
            sh.purchase_total = sum([x.pvp_total for x in sh.purchase_line_ids])

    @api.multi
    def update_workforce_cost(self):
        for sh in self:
            if sh.workforce_cost_ids:
                wfl = sh.workforce_cost_ids.filtered(lambda x: x.name == 'Horas Posprocesado')
                if wfl:
                    wfl.write({'hours': sh.total_oppi})

    @api.depends('use_treatment', 'material_cost_ids.material_id', 'tray_units')
    def _get_heat_treatment_cost(self):
        for sh in self:
            if sh.use_treatment and sh.material_cost_ids and  sh.tray_units:
                mat = sh.material_cost_ids[0].material_id
                ciclo = sh.cus_units / sh.tray_units
                sh.heat_treatment_cost = ciclo * mat.term_cost

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.group_id.update_sale_line_price()
        res.update_workforce_cost()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.mapped('group_id').update_sale_line_price()
        self.update_workforce_cost()
        return res

    @api.onchange('price_unit', 'cus_units')
    def change_inspection_type(self):
        if self.price_unit > 3000:
            self.inspection_type = 'tech'
        elif self.cus_units > 10:
            self.inspection_type = 'tech'
        elif self.cus_units > 0:
            self.inspection_type = 'visual'

    @api.onchange('sheet_type', 'material_cost_ids.material_id', 'machine_hours', 'printer_id')
    def onchange_sheet_type(self):
        # import ipdb; ipdb.set_trace()
        if not self.sheet_type or self.sheet_type in ['unplanned', 'meets', 'purchase']:
            return
        # options =  ['Horas Técnico', 'Horas Diseño', 'Horas Posprocesado']
        options =  ['Horas Técnico', 'Horas Posprocesado']
        out_options =  ['Insertos', 'Tornillos', 'Pintado', 'Accesorios', 'Otros']
        wf_lines = []
        out_lines = []
        # CREATE OUTSORCING LINES FOR ALL TYPES
        out_lines = [(5, 0, 0)]
        for name in out_options:
            vals = {'name': name, 'margin': 20.0}
            out_lines.append((0, 0, vals))
        # FDM CREATE WORKFORCE LINES
        wf_lines = [(5, 0, 0)]

        for name in options:
            hours = 0

            material = False
            maq_hours = 0.0
            if self.material_cost_ids:
                material = self.material_cost_ids[0].material_id
                tray_hours = self.tray_hours
                if self.sheet_type == 'sls':
                    tray_hours = self.tray_hours_sls
                if self.cus_units:
                    maq_hours = self.machine_hours
                    maq_hours = (tray_hours / self.tray_units) * self.cus_units
            if name == 'Horas Técnico' and material:
                if self.sheet_type == 'fdm':
                    hours = (5/60) + (maq_hours * self.printer_id.machine_hour * material.factor_hour)
                if self.sheet_type in ['sls', 'poly', 'sla', 'sls2', 'dmls']:
                    hours = (5/60) + (maq_hours * self.printer_id.machine_hour)
            # Mantener valores de horas diseño y postprocesado si ya existian
            elif self.workforce_cost_ids:
                wfl = self.workforce_cost_ids.filtered(
                    lambda x: x.name == name)
                if wfl:
                    hours = wfl.hours
            vals = {
                'name': name,
                'hours': hours,
            }
            wf_lines.append((0, 0, vals))
        # if not self.workforce_cost_ids:
        self.update({
            'workforce_cost_ids': wf_lines,
        })
        if not self.outsorcing_cost_ids:
            self.update({
                'outsorcing_cost_ids': out_lines,
            })

        # Poner impresoras por defecto
        if self.sheet_type and self.sheet_type != 'design' and \
                self.sheet_type != 'unplanned':
            srch_field = 'default_' + self.sheet_type
            domain = [(srch_field, '=', True)]
            printer = self.env['printer.machine'].search(domain)
            if printer:
                self.update({
                    'printer_id': printer.id,
                })

        if self.sheet_type in ['poly', 'sla', 'sls2']:
            self.cost_init = 20.0
        return {'domain': {'printer_id': [('type', '=', self.sheet_type)]}}


    @api.depends('price_total', 'cc_ud')
    def get_euros_cc_fdm(self):
        for sh in self:
            if sh.cc_ud:
                sh.euros_cc = sh.price_total / sh.cc_ud

    @api.multi
    def get_discount_qty(self):
        self.ensure_one
        if not self.use_disc_qty or not self.printer_id:
            return 0.0
        res = 0.0
        units = self.cus_units
        dmc = self.printer_id.max_disc_qty  # desc. max. qty
        dm = self.printer_id.discount  # max discount
        d2 = self.printer_id.discount2  # max discount
        if units < 2:
            res = 0.0
        elif units >= 2:
            if units < dmc:
                res = ( (dm - d2) / (dmc - 2) ) * (units - 2) + d2
            elif units >= dmc:
                res = dm
        return res

    def _get_cost_prices(self):
        for sh in self:
            cost = 0.0
            pvp = 0.0
            pu = 0.0
            disc_qty = sh.get_discount_qty()

            dq = sh.disc_qty / 100.0
            dqc = disc_qty / 100.0
            da = sh.disc2 / 100.0
            fa = sh.admin_fact / 100.0
            inc = sh.increment / 100.0

            if sh.sheet_type == 'design':
                cost = sh.amount_total
                pvp = cost * (1 - dq) * (1 - da) * (1 + fa)
            elif sh.sheet_type in ('fdm', 'sls', 'poly', 'sla', 'sls2',
                                   'dmls'):
                if sh.sheet_type == 'dmls':
                    cost_init_computed = 0
                    if sh.material_cost_ids and \
                            sh.material_cost_ids[0].material_id:
                        cost_init_computed = sh.material_cost_ids[0].\
                            material_id.init_cost
                        sh.cost_init_computed = cost_init_computed

                ci = sh.cost_init if sh.sheet_type not in ['fdm', 'dmls'] \
                    else sh.cost_init_computed

                num1 = (ci + sh.heat_treatment_cost) if \
                    sh.sheet_type == 'dmls' else ci
                cost = (
                    (num1 / sh.cus_units) +
                    (sh.total_euro_ud + sh.euro_machine_ud)*(1 - dqc) +
                    (sh.workforce_total_euro_ud + sh.outsorcing_total_ud +
                     sh.purchase_total))

                pu = cost * (1 + fa) * (1 + inc)
                pvp = pu * sh.cus_units

            elif sh.sheet_type == 'unplanned':
                pvp = sh.unplanned_cost
            elif sh.sheet_type == 'meets':
                pvp = sh.meet_total
            elif sh.sheet_type == 'purchase':
                pvp = sh.purchase_total

            sh.update({
                'cost_ud': cost,
                'disc_qty_computed': disc_qty,
                'price_unit': pu,
                'price_total': pvp})

    @api.depends('time_line_ids')
    def _get_totals_design(self):
        for sh in self:
            sh.hours_total = sum([x.hours for x in sh.time_line_ids])
            sh.amount_total = sum([x.total for x in sh.time_line_ids])

    @api.onchange('printer_id')
    def onchange_printer_id(self):
        res = {}
        options =  ['Extrusor 1', 'Extrusor 2', 'Extrusor 3']
        # TODO revisar
        if self.sheet_type == 'fdm':
            cost_lines = [(5, 0, 0)]
            for name in options:
                vals = {
                    'name': name,
                    'diameter': self.printer_id.diameter,
                }
                cost_lines.append((0, 0, vals))
            self.material_cost_ids = cost_lines
        return res

    @api.depends('price_total', 'cc_ud')
    def get_euros_cc_fdm(self):
        for sh in self:
            if sh.cc_ud:
                sh.euros_cc = sh.price_total / sh.cc_ud

    # @api.depends()
    def get_euro_machine(self):
        for sh in self:
            if sh.sheet_type == 'fdm':
                if sh.material_cost_ids and sh.printer_id and \
                        sh.material_cost_ids[0].material_id:
                    mat = sh.material_cost_ids[0].material_id
                    sh.euro_machine = sh.printer_id.euro_hour * mat.factor_hour
            elif sh.sheet_type in ['sls', 'poly', 'sla', 'sls2', 'dmls']:
                sh.euro_machine = sh.printer_id and sh.printer_id.euro_hour

    @api.depends('material_cost_ids')
    def _get_totals_material_cost(self):
        for sh in self:
            sh.total_euro_ud = sum(
                [x.euro_material for x in sh.material_cost_ids])
            sh.total_material_cost = sh.total_euro_ud * sh.cus_units

    @api.depends('tray_units', 'tray_hours', 'tray_hours_sls', 'cus_units', 
                 'euro_machine')
    def _get_fdm_machine_cost(self):
        for sh in self:
            tray_hours = sh.tray_hours
            if sh.sheet_type == 'sls':
                tray_hours = sh.tray_hours_sls
            if sh.cus_units:
                machine_hours = (tray_hours / sh.tray_units) * sh.cus_units
                sh.machine_hours = machine_hours
                euro_machine_ud = machine_hours * sh.euro_machine / sh.cus_units
                sh.euro_machine_ud = euro_machine_ud
                sh.euro_machine_total = euro_machine_ud * sh.cus_units

    @api.depends('workforce_cost_ids')
    def _get_totals_workforce(self):
        for sh in self:
            sh.workforce_total_euro_ud = \
                sum([x.euro_unit for x in sh.workforce_cost_ids])
            sh.workforce_total = sh.workforce_total_euro_ud * sh.cus_units


    @api.depends('outsorcing_cost_ids')
    def _get_totals_outsorcing(self):
        for sh in self:
            sh.outsorcing_total_ud = \
                sum([x.pvp for x in sh.outsorcing_cost_ids])
            sh.outsorcing_total = sh.outsorcing_total_ud * sh.cus_units

    @api.onchange('cus_units')
    def onchange_units_sls(self):
        for sh in self:
            sh.tray_units = sh.cus_units

    @api.depends('price_unit', 'cc_ud')
    def _get_e_cc_sls(self):
        for sh in self:
            if sh.cc_ud:
                sh.e_cc_sls = sh.price_unit / sh.cc_ud

    @api.onchange('cc_ud')
    def onchange_cc_ud(self):
        options = []
        material = False
        desviation = 0.0
        if self.sheet_type == 'fdm':
            return  # Está en el onchange print id
        elif self.sheet_type == 'sls':
            options = ['PA2200']
            material = self.env['product.product'].search(
                [('name', '=', options[0])])
        elif self.sheet_type == 'poly':
            options = ['Construccion', 'Soporte']
            material = False
        elif self.sheet_type == 'sla':
            options = ['Construccion']
            material = False
            desviation = 50.0
        elif self.sheet_type == 'sls2':
            options = ['Construccion']
            material = False
            desviation = 50.0
        elif self.sheet_type == 'dmls':
            options = [' ']
            material = False
            self.cc_soport_dmls = self.cc_ud * 0.3

        # CREATE MATERIAL COST LINES
        cost_lines = [(5, 0, 0)]
        for name in options:
            vals = {
                'name': name,
                'material_id': material.id if material else False,
                'desviation': desviation,
            }
            cost_lines.append((0, 0, vals))

        if not self.material_cost_ids:
            self.material_cost_ids = cost_lines

    # @api.depends('printer_id')
    def _get_sls_print_totals(self):
        for sh in self:
            if not sh.material_cost_ids:
                continue
            mat = sh.material_cost_ids[0].material_id
            if not mat:
                continue
            vel_cc = mat.vel_cc
            vel_z = mat.vel_z
            if not vel_cc or not vel_z:
                continue
            res = 0.0
            c7 = sh.tray_units
            d4 = sh.cc_ud
            f4 = sh.x_mm_sls
            d7 = sh.print_increment
            g4 = sh.y_mm_sls
            h4 = sh.z_mm_sls
            f10 = sh.bucket_height_sls
            d10 = sh.solid_per_sls / 100
            g10 = sh.simulation_time_sls
            if sh.offer_type == 'standard':
                if d4:
                    res = (c7*(d4/d4)*(d4/vel_cc+(((f4+d7)*(g4+d7)/(355*355))*((h4+d7))/10)/vel_z))
            elif sh.offer_type == 'xyz':
                res = (c7*((f4*g4*h4*d10/1000)/vel_cc+(((f4+d7)*(g4+d7))/(355*355))*((h4+d7)/10)/vel_z))
            elif sh.offer_type == 'cubeta':
                res = g10
            # sh.tray_hours_sls = 0.009850614743
            sh.tray_hours_sls = res

    @api.multi
    def create_tasks(self):
        """
        Create a task if sheet type is design, or if exist oppi line
        """
        design_sheets = self.filtered(lambda s: s.sheet_type == 'design')

        project = False
        if design_sheets:
            project = design_sheets.create_design_tasks()
            # if project:
            #     oppi_lines = self.mapped('oppi_line_ids').filtered(
            #         lambda x: not x.task_id)
            #     oppi_lines.create_oppi_tasks(project)
            if project:
                meet_lines = self.mapped('meet_line_ids').filtered(
                    lambda x: not x.task_id)
                meet_lines.create_meet_tasks(project)
        return

    @api.multi
    def create_sale_productions(self):
        design_sheets = self.filtered(lambda s: s.sheet_type == 'design')
        production_sheets = self - design_sheets

        if production_sheets:
            production_sheets.create_productions()
        return

    # @api.multi
    # def create_task_or_production(self):
    #     """
    #     Create a task if sheet type is design, or if exist oppi line
    #     or a production for each sheet.
    #     """
    #     design_sheets = self.filtered(lambda s: s.sheet_type == 'design')
    #     production_sheets = self - design_sheets

    #     project = False
    #     if design_sheets:
    #         project = design_sheets.create_tasks()
    #         if project:
    #             oppi_lines = self.mapped('oppi_line_ids').filtered(
    #                 lambda x: not x.task_id)
    #             oppi_lines.create_oppi_tasks(project)

    #     if production_sheets:
    #         production_sheets.create_productions()
    #     return

    @api.multi
    def manually_create_task_or_production(self):
        """
        Create a task if sheet type is design, or if exist oppi line
        or a production for each sheet.
        """
        if self.production_id:
            self.production_id.action_cancel()
            self.production_id.unlink()

        if self.sale_id.project_id:
            self.mapped('project_id.task_ids').unlink()
            self.mapped('project_id').unlink()

        self.create_tasks()
        self.create_sale_productions()
        return

    def create_design_tasks(self):
        order = self[0].sale_id
        vals = {
            'name': order.name,
            'partner_id': order.partner_id.id,
            'allow_timesheets': True,  # To create analytic account id
            'company_id': order.company_id.id,
            'sale_id': order.id
        }
        # CREATE PROJECT AND LNK WITH SALE
        project = self.env['project.project'].create(vals)
        # LINK SALE WITH PROJECT
        order.write({'project_id': project.id})
        for sheet in self:
            for line in sheet.time_line_ids:
                task_name = '[' + project.name + '] ' + 'OD - ' + sheet.sale_line_id.name
                if  line.software_id:
                    task_name += ' -> ' + line.software_id.name
                vals = {
                    'name': task_name,
                    'project_id': project.id,
                    'sheet_id': sheet.id,
                    'planned_hours': line.hours,
                    'time_line_id': line.id
                    # 'parent_id': task.id,
                }
                task = self.env['project.task'].create(vals)
                line.write({'task_id': task.id})
        return project

    def create_product_on_fly(self):
        self.ensure_one()
        vals = {
            'name': (self.name or '/'),
            'uom_id': 1,  # TODO get_unit
            'default_code': 'OF-' + (self.name or '/'),
            'type': 'product',
            'lst_price': self.price_total,
            'route_ids': [(6, 0, self.env.ref('mrp.route_warehouse0_manufacture').ids)],
            'active': False
        }
        product = self.env['product.product'].create(vals)
        self.product_id = product.id
        return product

    def create_components_on_fly(self):
        self.ensure_one()
        res = []
        for line in self.material_cost_ids.filtered('material_id'):
            vals = {
                'product_id': line.material_id.id,
                'product_qty': line.get_bom_qty(),  # TODO review,
                'product_uom_id': line.material_id.uom_id.id,
                'operation_id': False,
            }
            res.append((0,0, vals))

        for line in self.purchase_line_ids.filtered('product_id'):
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.qty,
                'product_uom_id': line.product_id.uom_id.id,
                'operation_id': False,
            }
            res.append((0,0, vals))
        return res

    def get_routing_on_fly(self):
        self.ensure_one()
        res = self.printer_id.routing_id
        if res and self.oppi_line_ids:
            new_routing = res.copy({'name': res.name + ' - ' + self.name})
            values = []
            for oppi in self.oppi_line_ids:
                vals = {
                    'name': oppi.name or '/',
                    'workcenter_id': oppi.type.workcenter_id.id,
                }
                values.append((0, 0, vals))
            new_routing.write({'operation_ids': values})
            res = new_routing
        return res

    def create_bom_on_fly(self, product):
        self.ensure_one()
        components = self.create_components_on_fly()
        routing = self.get_routing_on_fly()
        vals = {
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_qty': self.cus_units,  # TODO get_qty,
            'product_uom_id': product.uom_id.id,
            'type': 'normal',
            'bom_line_ids': components,
            'routing_id': routing and routing.id or False,
            'ready_to_produce': 'all_available'
        }
        bom = self.env['mrp.bom'].create(vals)

        return bom

    def create_productions(self):
        mrp_types = ['fdm', 'sls', 'poly', 'sla', 'sls2', 'dmls']
        for sheet in self.filtered(lambda sh: sh.sheet_type in mrp_types):
            product = sheet.create_product_on_fly()
            bom = sheet.create_bom_on_fly(product)
            vals = {
                'sheet_id': sheet.id,
                'product_id': sheet.product_id.id,
                'product_uom_id': sheet.product_id.uom_id.id,
                'product_qty': sheet.cus_units,  # TODO get_qty,
                'bom_id': bom.id,
                'date_planned_finished': 
                sheet.sale_line_id.order_id.production_date or False,
                # 'line_ref': sheet.sale_line_id.ref,
                # 'line_name': sheet.sale_line_id.name,
            }
            prod = self.env['mrp.production'].create(vals)
            prod.onchange_product_id()
            prod.button_plan()
            prod.workorder_ids.write({
                'duration_expected': sheet.machine_hours * 60,
                'date_planned_start': 
                sheet.sale_line_id.order_id.production_date,
                'date_planned_finished': 
                sheet.sale_line_id.order_id.production_date + 
                timedelta(hours=3),
            })
            sheet.write({'production_id': prod.id})
        return


class DesignTimeLine(models.Model):

    _name = 'design.time.line'

    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    software_id = fields.Many2one('design.software', 'Software')
    hours = fields.Float('Horas')
    price_hour = fields.Float('€/h')
    discount = fields.Float('Descuento')
    total = fields.Float('Total', compute="_compute_total")
    task_id = fields.Many2one(
        'project.task', 'Task', readonly=True, copy=False)

    @api.depends('hours', 'price_hour', 'discount')
    def _compute_total(self):
        for line in self:
            line.total = \
                line.hours * line.price_hour * (1 - line.discount / 100.0)

    @api.onchange('software_id')
    def onchange_doftware_id(self):
        for line in self:
            line.price_hour = line.software_id.price_hour


# FDM COSTE MATERIAL
class MaterialCostLine(models.Model):

    _name = 'material.cost.line'

    # COMUN
    name = fields.Char('Nombre', required=True)
    material_id = fields.Many2one('product.product', 'Material')

    euro_material = fields.Float('Euros Mat ud', compute='_compute_cost')
    total = fields.Float('Total', compute='_compute_cost')

    # FDM
    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    diameter = fields.Float('Diámetro')
    color = fields.Char('Color')
    tray_meters = fields.Float('Metros Bandeja')
    gr_cc_tray = fields.Float('gr o cc bandeja', compute='_compute_cost')
    gr_cc_total = fields.Float('gr o cc total', compute='_compute_cost')

    # SLS P396
    sls_gr_tray = fields.Float('Gr bandeja', compute='_compute_cost')
    sls_gr_total = fields.Float('Gr total', compute='_compute_cost')


    # POLY
    pol_gr_tray = fields.Float('Gr bandeja')
    pol_gr_total = fields.Float('Gr total', compute='_compute_cost')
    desviation = fields.Float('Desviation material', default=15.0)

    # SLA
    sla_cc_tray = fields.Float('cc bandeja')
    sla_cc_total = fields.Float('cc Total', compute='_compute_cost')

    # SLS
    sls2_cc_tray = fields.Float('cc bandeja')
    sls2_cc_total = fields.Float('cc Total', compute='_compute_cost')

    # DMLS
    dmls_cc_tray = fields.Float('gr bandeja', compute='_compute_cost')
    dmls_cc_total = fields.Float('gr Total', compute='_compute_cost')

    can_edit = fields.Boolean(related='sheet_id.can_edit')

    def get_sls_gr_tray(self):
        self.ensure_one()
        res = 0.0
        sh = self.sheet_id
        if not self.material_id:
            return 0.0
        c7 = sh.tray_units
        d4 = sh.cc_ud
        dens_cc = self.material_id.dens_cc
        f4 = sh.x_mm_sls
        d7 = sh.print_increment
        g4 = sh.y_mm_sls
        h4 = sh.z_mm_sls
        dens_bulk = self.material_id.dens_bulk
        f10 = sh.bucket_height_sls
        d10 = sh.solid_per_sls / 100
        if sh.offer_type == 'standard':
            if d4:
                res = (c7*(d4/d4))*(d4*dens_cc+(((f4+d7)*(g4+d7)*(h4+d7)/1000)-d4)\
                    * dens_bulk)
        elif sh.offer_type == 'xyz':
            res = c7*((f4*g4*h4*d10/1000)*dens_cc+(((f4+d7)*(g4+d7)*(h4+d7)/1000) - (f4*g4*h4*d10/1000))*dens_bulk)
        elif sh.offer_type == 'cubeta':
            if d4:
                res = (d4/d4)*((c7*d4*dens_cc)+((35.5*35.5*(1+f10)-(c7*d4))*dens_bulk))
        return res

    def _compute_cost(self):
        for mcl in self:
            if not mcl.material_id or not mcl.sheet_id:
                continue
            mat = mcl.material_id
            sh = mcl.sheet_id
            if sh.sheet_type == 'fdm':
                gr_cc_tray = (mat.gr_cc * math.pi * ((mcl.diameter / 2.0) ** 2)) * mcl.tray_meters
                mcl.gr_cc_tray = round(gr_cc_tray)
                if sh.cus_units:
                    gr_cc_total = (gr_cc_tray / sh.tray_units) * sh.cus_units
                    mcl.gr_cc_total = round(gr_cc_total)
                    euro_material = (mat.euro_kg * (gr_cc_total / 1000.0)) / sh.cus_units
                    mcl.euro_material = euro_material
            elif sh.sheet_type == 'sls':  # SLS P396
                sls_gr_tray = mcl.get_sls_gr_tray()
                mcl.sls_gr_tray = round(sls_gr_tray)
                if sh.tray_units:
                    sls_gr_total = (sls_gr_tray * sh.cus_units) / sh.tray_units
                    mcl.sls_gr_total = round(sls_gr_total)
                    euro_material = (sls_gr_tray * (mat.euro_kg_bucket / 1000.0)) / sh.tray_units
                    mcl.euro_material = euro_material
                    mcl.total = sh.cus_units * euro_material
            elif sh.sheet_type == 'poly':
                dis = mcl.desviation / 100
                if sh.tray_units:
                    mcl.pol_gr_total = ((1 + dis) * mcl.pol_gr_tray * sh.cus_units) / sh.tray_units
                    euro_material = (mcl.pol_gr_total * mat.euro_kg) / sh.cus_units
                    mcl.euro_material = euro_material
                    mcl.total = sh.cus_units * euro_material
            elif sh.sheet_type == 'sla':  # SLA
                dis = mcl.desviation / 100
                if sh.tray_units:
                    mcl.sla_cc_total = ((1 + dis) * mcl.sla_cc_tray * sh.cus_units) / sh.tray_units
                    euro_material = (mcl.sla_cc_total * mat.euro_cc) / sh.cus_units
                    mcl.euro_material = euro_material
                    mcl.total = sh.cus_units * euro_material
            elif sh.sheet_type == 'sls2':  # SLS
                dis = mcl.desviation / 100
                if sh.tray_units:
                    mcl.sls2_cc_total = ((1 + dis) * mcl.sls2_cc_tray * sh.cus_units) / sh.tray_units
                    euro_material = (mcl.sls2_cc_total * mat.euro_kg * mat.gr_cc) / sh.cus_units
                    mcl.euro_material = euro_material
                    mcl.total = sh.cus_units * euro_material

            elif sh.sheet_type == 'dmls':
                dis = mcl.desviation / 100
                if sh.tray_units:
                    e10 = mcl.desviation / 100.0
                    dmls_cc_tray = (sh.cc_ud+sh.cc_soport_dmls)*(1+e10)*sh.tray_units*mcl.material_id.dens_cc
                    mcl.dmls_cc_tray = round(dmls_cc_tray)
                    dmls_cc_total = ((1 + dis) * dmls_cc_tray * sh.cus_units) / sh.tray_units
                    mcl.dmls_cc_total = round(dmls_cc_total)
                    if sh.cus_units:
                        mcl.euro_material = ( mcl.dmls_cc_total * mat.euro_kg) / (sh.cus_units * 1000)
                        mcl.total = sh.cus_units * mcl.euro_material

    def get_bom_qty(self):
        self.ensure_one()
        sh = self.sheet_id
        res = 1.0
        if sh.sheet_type == 'fdm':
            res = self.gr_cc_tray
        elif sh.sheet_type == 'sls':
            res = self.sls_gr_tray

        elif sh.sheet_type == 'poly':
            res = self.pol_gr_tray

        elif sh.sheet_type == 'sla':
            res = self.sla_cc_tray

        elif sh.sheet_type == 'sls2':
            res = self.sls2_cc_tray

        elif sh.sheet_type == 'dmls':
           res = self.dmls_cc_tray
        return res


# FDM COSTE MANO DE OBRA
class WorkforceCostLine(models.Model):

    _name = 'workforce.cost.line'

    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    name = fields.Char('Nombre')
    hours = fields.Float('Horas')
    minutes = fields.Float('Minutos', compute="compute_workforce_totals")
    euro_unit = fields.Float('€ ud', compute="compute_workforce_totals")
    total = fields.Float('€ Total', compute="compute_workforce_totals")

    @api.depends('hours')
    def compute_workforce_totals(self):
        for wcl in self:
            sh = wcl.sheet_id
            hours2 = sh.group_id.tech_hours
            hours = wcl.hours
            maq_hours = sh.machine_hours
            if wcl.name == 'Horas Técnico' and sh.sheet_type in ['sls', 'poly', 'sla', 'sls2', 'dmls']:
                hours = (5/60) + (maq_hours * sh.printer_id.machine_hour)
            # if wcl.name == 'Horas Diseño':
            #      hours2 = sh.group_id.ing_hours
            if sh.cus_units:
                euro_unit = hours * hours2 / sh.cus_units
                wcl.euro_unit = euro_unit
                wcl.total = euro_unit * sh.cus_units
            wcl.minutes = wcl.hours * 60.0


# Coste externalizacion por piezaS
class OutsorcingCostLine(models.Model):

    _name = 'outsorcing.cost.line'

    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')

    name = fields.Char('Tarea')
    cost = fields.Float('Coste')
    margin = fields.Float('Margen (%)', default=20.0)
    pvp = fields.Float('PVP ud', compute="_get_pvp")

    @api.depends('cost', 'margin')
    def _get_pvp(self):
        for ocl in self:
            ocl.pvp = ocl.cost * (1 + ocl.margin / 100.0)


class MeetCostLine(models.Model):

    _name = 'meet.cost.line'

    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    type = fields.Selection([('visit', 'Visita'), ('meets', 'Reunión'),
                             ('call', 'Conferencia')], 'Tipo', default='visit')
    name = fields.Char('Nombre')
    num_people = fields.Float('Nº personas')
    hours = fields.Float('Tiempo')
    kms = fields.Float('Kms', default=0.0)
    pvp = fields.Float('PVP ud', compute="_get_pvp")
    task_id = fields.Many2one('project.task', 'Task', readonly=True,
                              copy=False)

    @api.depends('num_people', 'hours', 'kms')
    def _get_pvp(self):
        for mcl in self:
            ing_hours = mcl.sheet_id.group_id.ing_hours
            km_cost = mcl.sheet_id.group_id.km_cost
            pvp = (mcl.num_people * mcl.hours * ing_hours)
            if mcl.type == 'visit':
                pvp += (mcl.kms * km_cost)
            mcl.pvp = pvp

    def create_meet_tasks(self, project):
        for line in self:
            if line.task_id:
                continue
            line_name = line.name if line.name else ''
            vals = {
                'name': "[" + project.name + '] ' + 'REUNIÓN - ' + line_name,
                'project_id': project.id,
                'sheet_id': line.sheet_id.id,
                'meet_line_id': line.id,
                'planned_hours': line.hours,
                # 'user_id': line.employee_id.user_id.id
            }
            # Lo hago con sudo , porque me falla con el employye_id admin,
            # un posible error de seguridad
            task = self.env['project.task'].sudo().create(vals)
            line.write({'task_id': task.id})


class PurchaseCostLine(models.Model):

    _name = 'purchase.cost.line'

    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')

    product_id = fields.Many2one('product.product', 'Producto')
    name = fields.Char('Ref. / Descripción')
    qty = fields.Float('Unidades')
    partner_id = fields.Many2one(
        'res.partner', 'Proveedor', required=True, domain=[('supplier', '=', True)])
    cost_ud = fields.Float('Coste Ud.')
    ports = fields.Float('Portes')
    margin = fields.Float('Margin (%)', default=30.0)
    pvp_ud = fields.Float('PVP Ud', compute="_get_pvp")
    pvp_total = fields.Float('PVP TOTAL', compute="_get_pvp")

    @api.depends('qty', 'cost_ud', 'ports', 'margin')
    def _get_pvp(self):
        for ocl in self:
            pvp_ud = 0.0
            pvp = 0.0
            if ocl.qty:
                pvp_ud = ocl.cost_ud * (1 + (ocl.margin/100)) + \
                    (ocl.ports / ocl.qty)
                pvp = pvp_ud * ocl.qty
            ocl.pvp_ud = pvp_ud
            ocl.pvp_total = pvp

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.cost_ud = self.product_id.standard_price


class OppiCostLine(models.Model):

    _name = 'oppi.cost.line'

    sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')

    name = fields.Char('Descripción', required=True)
    type = fields.Many2one('oppi.type', 'Tipo', required=True)
    time = fields.Float('Tiempo')
    time_real = fields.Float('Tiempo real', related='task_id.effective_hours')
    employee_id = fields.Many2one('hr.employee', 'Empleado')
    task_id = fields.Many2one('project.task', 'Task', readonly=True,  
                              copy=False)

    def create_oppi_tasks(self, project):
        for line in self:
            if line.task_id:
                continue
            line_name = line.name if line.name else ''
            vals = {
                'name': "[" + project.name + '] ' + 'OPPI - ' + line_name,
                'project_id': project.id,
                'sheet_id': line.sheet_id.id,
                'oppi_line_id': line.id,
                'planned_hours': line.time,
                'user_id': line.employee_id.user_id.id
            }
            # Lo hago con sudo , porque me falla con el employye_id admin,
            # un posible error de seguridad
            task = self.env['project.task'].sudo().create(vals)
            line.write({'task_id': task.id})