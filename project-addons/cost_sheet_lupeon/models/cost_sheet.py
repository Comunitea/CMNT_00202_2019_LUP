# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
import math


SHEET_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS'),
    ('sla', 'SLA'),
    ('dmls', 'DMLS'),
    ('oppi', 'OPPI'),
]

class GroupCostSheet(models.Model):

    _name = 'group.cost.sheet'
    _rec_name = 'sale_line_id'

    # display_name = fields.Char('Name', readonly="True")
    sale_line_id = fields.Many2one('sale.order.line', 'Línea de venta', 
                                   readonly=False)
    product_id = fields.Many2one('product.product', 'Producto', 
        related='sale_line_id.product_id')
    admin_fact = fields.Float('Factor administrativo')

    ing_hours = fields.Integer('Horas ingenieria', default=55)
    tech_hours = fields.Integer('Horas técnico', default=35)
    help_hours = fields.Integer('Horas ayudante', default=35)
    sheet_ids = fields.One2many(
        'cost.sheet', 'group_id', string='Cost Sheets')
    line_pvp = fields.Float('PVP Línea', compute='_get_line_pvp')
    
    def name_get(self):
        res = []
        for sheet in self:
            res.append((sheet.id, ("[%s] %s") % \
                (sheet.sale_line_id.order_id.name, 
                 sheet.sale_line_id.name)))
        return res
    
    def update_sale_line_price(self):
        for group in self:
            group.sale_line_id.write({'price_unit': group.line_pvp})
    
    
    @api.depends('sheet_ids')
    def _get_line_pvp(self):
        for group in self:
            pvp = sum(group.sheet_ids.mapped('price_total'))
            group.line_pvp = sum([x.price_total for x in group.sheet_ids])


class CostSheet(models.Model):

    _name = 'cost.sheet'

    # COMUN
    name = fields.Char('Referencia')
    group_id = fields.Many2one('group.cost.sheet', 'Hojas de coste',
                               required=True, ondelete="cascade", 
                               readonly=True)
    task_id = fields.Many2one(
        'project.task', 'Orden de diseño', index=True, copy=False,
        readonly=True)
    production_id = fields.Many2one(
        'mrp.production', 'Produción', index=True, copy=False,
        readonly=True)

    sheet_type = fields.Selection(SHEET_TYPES, 'Tipo de hoja')

    sale_line_id = fields.Many2one('sale.order.line', 'Línea de venta',
        related='group_id.sale_line_id', store=True, readonly=True)
    sale_id = fields.Many2one('sale.order', 'Pedido de venta',
        related='group_id.sale_line_id.order_id', store=True, readonly=True)
    
    init_cost = fields.Float('Coste', compute="_get_cost_prices")
    admin_fact = fields.Float('Factor administrativo', 
        related='group_id.admin_fact')
    disc_qty = fields.Float('Descuento cantidad')
    disc_qty_computed = fields.Float('Descuento cantidad', compute='_get_cost_prices')
    disc2 = fields.Float('Descuento adicional')
    increment = fields.Float('Incremento no estándar')
    inspection_type = fields.Selection(
        [('visual', 'Visual'), ('tech', 'Technical')], string="Tipo de inspeción")
    price_unit = fields.Float('PVP unidad', compute='_get_cost_prices')
    price_total = fields.Float('PVP TOTAL', compute='_get_cost_prices')

    # @api.depends()
    def _get_cost_prices(self):
        for sh in self:
            cost = 0.0
            pvp = 0.0
            pu = 0.0
            disc_qty = 0.0

            dq = sh.disc_qty / 100.0
            da = sh.disc2 / 100.0
            fa = sh.admin_fact / 100.0
            if sh.sheet_type == 'design':
                cost = round(sh.amount_total, 2)
                
                # pvp = cost * (1 - dq - da + fa)
                pvp = round(cost * (1 - dq)* (1 - da) * (1+ fa), 2)
            elif sh.sheet_type == 'fdm':
                sum_wf_costs = sh.workforce_total_euro_ud
                cost = round(sh.total_euro_ud + sh.euro_machine_ud + sum_wf_costs + sh.outsorcing_total_ud, 2)
                disc_qty = 3.75  # TODO calculo complejo en funcion de campo boolean
                dqc = disc_qty / 100.0
                pu = round(cost * (1 - dqc + da + fa), 2)
                pu = round(cost * (1 - dqc)* (1 + da) * (1+ fa), 2)
                pvp = round(pu * sh.cus_units, 2)
            elif sh.sheet_type == 'sls':
                pvp = 0
            elif sh.sheet_type == 'sla':
                pvp = 0
            elif sh.sheet_type == 'dmls':
                pvp = 0
            elif sh.sheet_type == 'opi':
                pvp = 0
            
            sh.update({
                'init_cost': cost,
                'disc_qty_computed': disc_qty,
                'price_unit': pu,
                'price_total': pvp})

    #PROPIOS DE DISEÑO
    flat_ref = fields.Char('Plano')
    legislation_ids = fields.Many2many(
        'applicable.legislation',
        'cost_sheet_applicable_legislation_rel',
        'sheet_id', 'legislation_id',
        string='Legislación aplicable')
    time_line_ids = fields.One2many('design.time.line', 'sheet_id', string='Tiempos')
    description = fields.Text('Requisitos técnicos')
    customer_note = fields.Text('Comentarios Cliente')
    hours_total = fields.Float('Horas totales', compute="_get_totals_design")
    amount_total = fields.Float('Importe TOTAL', compute="_get_totals_design")

    @api.depends('time_line_ids')
    def _get_totals_design(self):
        for sh in self:
            sh.hours_total = sum([x.hours for x in sh.time_line_ids])
            sh.amount_total = sum([x.total for x in sh.time_line_ids])

    # ------------------------------------------------------------------------

    # FDM DATOS PIEZA
    cus_units = fields.Integer('Uds. Cliente')
    cc_ud_fdm = fields.Integer('cc ud')
    stat_data = fields.Char('Dato estadístico')
    euros_cc = fields.Float('€/cc', compute='get_euros_cc_fdm')

    @api.depends('price_total', 'cc_ud_fdm')
    def get_euros_cc_fdm(self):
        for sh in self:
            if sh.cc_ud_fdm:
                sh.euros_cc = sh.price_total / sh.cc_ud_fdm
    
    # FDM PARÁMETROS IMPRESIÓN
    printer_id = fields.Many2one(
        'printer.machine', 'Impresora', domain=[('type', '=', 'fdm')])
    tray_units = fields.Integer('Uds. Bandeja')
    infill = fields.Float('Infill')  # Model or selection?
    loops = fields.Integer('Loops') # Model or selection?
    layer_height = fields.Float('Altura de Capa') # Model or selection?
    tray_hours = fields.Float('h Maq. Bandeja')
    euro_machine = fields.Float('€/h maq',  compute='get_euro_machine_fdm')
    perfil = fields.Char('Perfil')

    @api.onchange('printer_id')
    def onchange_printer_id(self):
        options =  ['Extrusor 1', 'Extrusor 2', 'Extrusor 3']
        for sh in self:
            cost_lines = [(5, 0, 0)]
            for name in options:
                vals = {
                    'name': name,
                    'diameter': sh.printer_id.diameter,
                }
                cost_lines.append((0, 0, vals))
            sh.material_cost_ids = cost_lines
    
    @api.onchange('sheet_type', 'material_cost_ids')
    def onchange_sheet_type(self):
        options =  ['Horas Técnico', 'Horas Diseño', 'Horas Posprocesado']
        out_options =  ['Insertos', 'Tornillos', 'Pintado', 'Accesorios', 'Otros']
        wf_lines = []
        out_lines = []
        # sls_out_lines = []
        for sh in self:
            # CREATE OUTSORCING LINES FOR ALL TYPES
            out_lines = [(5, 0, 0)]
            for name in out_options:
                vals = {'name': name, 'margin': 20.0}
                out_lines.append((0, 0, vals))
            if sh.sheet_type == 'fdm':
                # FDM REATE WORKFORCE LINES
                wf_lines = [(5, 0, 0)]

                for name in options:
                    hours = 0
                    if name == 'Horas Técnico' and sh.material_cost_ids and sh.material_cost_ids[0].material_id:
                        mat = sh.material_cost_ids[0].material_id
                        hours = 5/60 + sh.machine_hours * sh.printer_id.machine_hour * mat.factor_hour
                    vals = {
                        'name': name,
                        'hours': hours,
                    }
                    wf_lines.append((0, 0, vals))
            
            sh.update({
                'workforce_cost_ids': wf_lines,
                'outsorcing_cost_ids': out_lines,
            })



    @api.depends('price_total', 'cc_ud_fdm')
    def get_euros_cc_fdm(self):
        for sh in self:
            if sh.cc_ud_fdm:
                sh.euros_cc = sh.price_total / sh.cc_ud_fdm
    
    # @api.depends()
    def get_euro_machine_fdm(self):
        for sh in self:
            if sh.material_cost_ids and sh.printer_id and sh.material_cost_ids[0].material_id:
                mat = sh.material_cost_ids[0].material_id
                sh.euro_machine = sh.printer_id.euro_hour * mat.factor_hour

    # FDM COSTE MATERIAL
    material_cost_ids = fields.One2many(
        'material.cost.line', 'fdm_sheet_id', string='Coste material')
    total_euro_ud = fields.Float('Total € ud', compute='_get_totals_material_cost')
    total_material_cost = fields.Float('Total', compute='_get_totals_material_cost')

    @api.depends('material_cost_ids')
    def _get_totals_material_cost(self):
        for sh in self:
            sh.total_euro_ud = round(sum(
                [x.euro_material for x in sh.material_cost_ids]),2)
            sh.total_material_cost = sh.total_euro_ud * sh.cus_units
    
    # FDM COSTE MÁQUINA
    machine_hours = fields.Float('Horas Maq total', 
        compute='_get_fdm_machine_cost')
    euro_machine_ud = fields.Float('Euros Maq ud', 
        compute='_get_fdm_machine_cost')  
    euro_machine_total = fields.Float('Euros Maq total', 
        compute='_get_fdm_machine_cost')

    @api.depends('tray_units', 'tray_hours', 'cus_units', 'euro_machine')
    def _get_fdm_machine_cost(self):
        for sh in self:
            if sh.cus_units:
                sh.machine_hours = sh.tray_hours / sh.tray_units * sh.cus_units
                sh.euro_machine_ud = 0.0
                sh.euro_machine_ud = sh.machine_hours * sh.euro_machine / sh.cus_units
                sh.euro_machine_total = sh.euro_machine_ud * sh.cus_units

    # FDM COSTE MANO DE OBRA
    workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'fdm_sheet_id', string='Coste Mano de obra')
    workforce_total_euro_ud = fields.Float(
        'Total € ud', compute="_get_totals_workforce")
    workforce_total = fields.Float(
    'Total', compute="_get_totals_workforce")

    @api.depends('outsorcing_cost_ids')
    def _get_totals_workforce(self):
        for sh in self:
            sh.workforce_total_euro_ud = sum([x.euro_unit for x in sh.workforce_cost_ids])
            sh.workforce_total =sh.total_euro_ud * sh.cus_units
    
    # FDM COSTE EXTERNALIZACION POR PIEZA
    outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'fdm_sheet_id', string='Coste externalizacion por pieza')
    outsorcing_total_ud = fields.Float(
        'Total ud', compute="_get_totals_outsorcing")
    outsorcing_total = fields.Float(
    'Total', compute="_get_totals_outsorcing")

    @api.depends('outsorcing_cost_ids')
    def _get_totals_outsorcing(self):
        for sh in self:
            sh.outsorcing_total_ud = sum([x.pvp for x in sh.outsorcing_cost_ids])
            sh.outsorcing_total =sh.outsorcing_total_ud * sh.cus_units


    # FDM PART FEATURES
    feature_ids = fields.Many2many(
        'part.feature',
        'cost_sheet_paer_features_rel',
        'sheet_id', 'feature_id',
        string='Características pieza')
    
    # ------------------------------------------------------------------------
    
    # SLS DATOS PIEZA
    cus_units = fields.Integer('Uds. Cliente')
    cc_und_sls = fields.Integer('cc ud')
    cm2_sls = fields.Float('cm^2 ud')
    x_mm_sls = fields.Float('X (mm)')
    y_mm_sls = fields.Float('Y (mm)')
    z_mm_sls = fields.Float('Z (mm)')
    static_data_sls = fields.Char('Dato estadístico')
    e_cc_sls = fields.Float('€/cc', compute="_get_e_cc_sls")

    @api.onchange('cus_units')
    def onchange_units_sls(self):
        for sh in self:
            sh.tray_units = sh.cus_units

    @api.depends('price_unit', 'cc_und_sls')
    def _get_e_cc_sls(self):
        for sh in self:
            if sh.cc_und_sls:
                sh.e_cc_sls = sh.price_unit / sh.cc_und_sls
    
    @api.onchange('cc_und_sls')
    def onchange_cc_und_sls(self):
        options = ['PA2200']
        material = self.env['material'].search([('name', '=', options[0])])
        for sh in self:
            cost_lines = [(5, 0, 0)]
            for name in options:
                vals = {
                    'name': name,
                    'material_id': material.id if material else False
                }
                cost_lines.append((0, 0, vals))
            sh.sls_material_cost_ids = cost_lines

            # CREATE WORKFORCE LINES
            sls_wf_lines = [(5, 0, 0)]

            for name in options:
                hours = 0
                if name == 'Horas Técnico' and sh.material_cost_ids and sh.material_cost_ids[0].material_id:
                    mat = sh.material_cost_ids[0].material_id
                    hours = 5/60 + sh.machine_hours * sh.printer_id.machine_hour * mat.factor_hour
                vals = {
                    'name': name,
                    'hours': hours,
                }
                sls_wf_lines.append((0, 0, vals))
                sh.sls_workforce_cost_ids = sls_wf_lines

    # SLS PARÁMETROS IMPRESIÓN
    increment_sls = fields.Float('Incremento (mm)', default=18.0)
    tray_hours_sls = fields.Float('h Maq. Bandeja', compute='_get_sls_print_totals', digits=(16, 4))
    euro_machine_sls = fields.Float('€/h maq', compute='_get_sls_print_totals')
    
    @api.depends('printer_id')
    def _get_sls_print_totals(self):
        for sh in self:
            sh.tray_hours_sls = 0.052 # TODO
            sh.euro_machine_sls = sh.printer_id and sh.printer_id.euro_hour


    # SLS OFERT CONFIGURATION
    offer_type = fields.Selection(
        [('standard', 'Standard'),
         ('xyz', 'XYZ'),
         ('cubeta', 'Cubeta')], 'Tipo oferta', default='standard')
    solid_per_sls = fields.Float('% Solido', default=80.0)
    bucket_height_sls = fields.Float('Altura cubeta')
    simulation_time_sls = fields.Float('Tiempo impresión simulacion')

    # SLS MATERIAL COST
    sls_material_cost_ids = fields.One2many(
        'material.cost.line', 'sls_sheet_id', string='Coste material')

    # SLS COSTE MÁQUINA
    machine_hours_sls = fields.Float('Horas Maq total', compute="_get_sls_machine_cost")
    euro_machine_ud_sls = fields.Float('Euros Maq ud', compute="_get_sls_machine_cost")  
    euro_machine_total_sls = fields.Float('Euros Maq total', compute="_get_sls_machine_cost")

    @api.depends('tray_units', 'tray_hours_sls', 'cus_units', 'euro_machine_sls')
    def _get_sls_machine_cost(self):
        for sh in self:
            if sh.cus_units:
                sh.machine_hours_sls = sh.tray_hours_sls / sh.tray_units * sh.cus_units
                sh.euro_machine_ud_sls = sh.machine_hours_sls * sh.euro_machine_sls / sh.cus_units
                sh.euro_machine_total_sls = sh.euro_machine_ud_sls * sh.cus_units

    # SLS COSTE MANO DE OBRA
    sls_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sls_sheet_id', string='Coste material')
    
    # SLS COSTE EXTERNALIZACION POR PIEZA
    tinted_sls = fields.Selection(
        [('blue', 'Blue'),
         ('black', 'XYZ'),
         ('no_tinted', 'No tinted'),
         ('other', 'Other colors')], 'Tintado')

    # ------------------------------------------------------------------------ 

    # POLY DATOS PIEZA
    units_pol = fields.Integer('Uds. Cliente')
    cc_und_pol = fields.Integer('cc ud')
    stat_data_pol = fields.Char('Dato estadístico')
    euros_cc_pol = fields.Float('€/cc')

    # POLY PARÁMETROS IMPRESIÓN
    tray_units_pol = fields.Integer('Uds. Bandeja')
    finish_pol = fields.Selection([
        ('glossy', 'Glossy'),
        ('mate', 'Mate')], 'Acabado')
    tray_hours_pol = fields.Float('h Maq. Bandeja')
    euro_machine_pol = fields.Float('€/h maq')

    # POLY MATERIAL COST
    pol_material_cost_ids = fields.One2many(
        'material.cost.line', 'pol_sheet_id', string='Coste material')

    # POLY COSTE MÁQUINA
    machine_hours_pol = fields.Float('Horas Maq total')
    euro_machine_ud_pol = fields.Float('Euros Maq ud')  
    euro_machine_total_pol = fields.Float('Euros Maq total')

    # POLY COSTE MANO DE OBRA
    pol_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'pol_sheet_id', string='Coste material')

    # POLY COSTE EXTERNALIZACION POR PIEZA

    # ------------------------------------------------------------------------- 

    # SLA DATOS PIEZA
    units_sla = fields.Integer('Uds. Cliente')
    cc_und_sla = fields.Integer('cc ud')
    stat_data_sla = fields.Char('Dato estadístico')
    euros_cc_sla = fields.Float('€/cc')

    # SLA PARÁMETROS IMPRESIÓN
    tray_units_sla = fields.Integer('Uds. Bandeja')
    tray_hours_sla = fields.Float('h Maq. Bandeja')
    euro_machine_sla = fields.Float('€/h maq')

    # SLA MATERIAL COST
    sla_material_cost_ids = fields.One2many(
        'material.cost.line', 'sla_sheet_id', string='Coste material')

    # SLA COSTE MÁQUINA
    machine_hours_sla = fields.Float('Horas Maq total')
    euro_machine_ud_sla = fields.Float('Euros Maq ud')  
    euro_machine_total_sla = fields.Float('Euros Maq total')

    # SLA COSTE EXTERNALIZACION POR PIEZA

    # SLA COSTE MANO DE OBRA
    sla_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sla_sheet_id', string='Coste material')
    
    # ------------------------------------------------------------------------- 

    # DMLS DATOS PIEZA
    units_dmls = fields.Integer('Uds. Cliente')
    cc_und_dmls = fields.Integer('cc ud')
    cc_soport = fields.Integer('cc soporte')
    stat_data_dmls = fields.Char('Dato estadístico')
    euros_cc_dmls = fields.Float('€/cc')

    # dmls PARÁMETROS IMPRESIÓN
    tray_units_dmls = fields.Integer('Uds. Bandeja')
    tray_hours_dmls = fields.Float('h Maq. Bandeja')
    euro_machine_dmls = fields.Float('€/h maq')

    # dmls MATERIAL COST
    dmls_material_cost_ids = fields.One2many(
        'material.cost.line', 'sla_sheet_id', string='Coste material')

    # dmls COSTE MÁQUINA
    machine_hours_dmls = fields.Float('Horas Maq total')
    euro_machine_ud_dmls = fields.Float('Euros Maq ud')  
    euro_machine_total_dmls = fields.Float('Euros Maq total')

    # dmls COSTE EXTERNALIZACION POR PIEZA
 
    # dmls COSTE MANO DE OBRA
    dmls_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sla_sheet_id', string='Coste mano de obra')
    
   
    @api.model
    def create(self, vals):
       res = super().create(vals)
       res.group_id.update_sale_line_price()
       return res
    
    def write(self, vals):
       res = super().write(vals)
       self.mapped('group_id').update_sale_line_price()
       return res
    
    
    # LÓGICA
    @api.multi
    def create_task_or_production(self):
        """
        Create a task if sheet type is design,
        or a production for each sheet.
        """
        design_sheets = self.filtered(lambda s: s.sheet_type == 'design')
        production_sheets = self - design_sheets

        if design_sheets:
            design_sheets.create_tasks()

        if production_sheets:
            production_sheets.create_productions()
        return
    
    def create_tasks(self):
        order = self[0].sale_id
        vals = {
            'name': 'OD - ' + order.name,
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
            vals = {
                'name': "[" + project.name + '] ' + 'OD - ' + sheet.sale_line_id.name,
                'project_id': project.id,
                'sheet_id': sheet.id
            }
            task = self.env['project.task'].create(vals)
            sheet.write({'task_id': task.id})
        return

    def create_productions(self):
        for sheet in self:
            line = sheet.sale_line_id
            bom = self.env['mrp.bom']._bom_find(product=line.product_id)
            vals = {
                # 'name': "[" + line.order_id.name + '] ' + line.name,
                'sheet_id': sheet.id,
                'product_id':line.product_id.id,
                'product_uom_id':line.product_id.uom_id.id,
                'product_qty': 1,
                'bom_id': bom.id
            }
            prod = self.env['mrp.production'].create(vals)
            prod.onchange_product_id()
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
    name = fields.Char('Nombre')
    material_id = fields.Many2one('material', 'Material')
    gr_tray = fields.Float('Gr bandeja')
    gr_total = fields.Float('Gr total')
    total = fields.Float('Total')

    # FDM
    fdm_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    diameter = fields.Float('Diámetro')
    color = fields.Char('Color')
    tray_meters = fields.Float('Metros Bandeja')
    gr_cc_tray = fields.Float('gr o cc bandeja', compute='_compute_cost_fdm')
    gr_cc_total = fields.Float('gr o cc total', compute='_compute_cost_fdm')
    euro_material = fields.Float('Euros Mat ud', compute='_compute_cost_fdm')

    @api.depends('material_id', 'tray_meters')
    def _compute_cost_fdm(self):
        for mcl in self:
            if not mcl.material_id or not mcl.fdm_sheet_id:
                continue
            mat = mcl.material_id
            sh = mcl.fdm_sheet_id
            mcl.gr_cc_tray = round(mat.gr_cc * math.pi * ((mcl.diameter / 2.0) ** 2) * mcl.tray_meters)
            if sh.cus_units:
                mcl.gr_cc_total = round(mcl.gr_cc_tray / sh.cus_units * sh.tray_units)
                mcl.euro_material = mat.euro_kg * (mcl.gr_cc_total / 1000.0) / sh.cus_units
    
    # SLS
    sls_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    sls_gr_tray = fields.Float('Gr bandeja', compute='_compute_cost_sls')
    sls_gr_total = fields.Float('Gr total', compute='_compute_cost_sls')
    sls_euro_material = fields.Float('Euros Mat ud', compute='_compute_cost_sls')
    sls_total = fields.Float('Total', compute='_compute_cost_sls')
    
    # @api.depends('material_id')
    def _compute_cost_sls(self):
        for mcl in self:
            if not mcl.material_id or not mcl.sls_sheet_id:
                continue
            sh = mcl.sls_sheet_id
            mat = mcl.material_id
            mcl.sls_gr_tray = 25 # TODO
            if sh.tray_units:
                mcl.sls_gr_total = (mcl.sls_gr_tray * sh.cus_units) / sh.tray_units
            if sh.tray_units:
                mcl.sls_euro_material = (mcl.sls_gr_tray * (mat.euro_kg_bucket / 1000.0)) / sh.tray_units
            mcl.sls_total = sh.cus_units * mcl.sls_euro_material
    # POLY
    pol_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')

    # SLA
    sla_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    desviation = fields.Float('Desviation material')
    cc_tray = fields.Float('cc bandeja')
    cc_total = fields.Float('cc Total')

    # DMLS
    dmls_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')


# FDM COSTE MANO DE OBRA
class WorkforceCostLine(models.Model):

    _name = 'workforce.cost.line'

    fdm_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    sls_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    pol_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    sla_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    dmls_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    name = fields.Char('Nombre')
    hours = fields.Float('Horas')
    minutes = fields.Float('Minutos', compute="compute_workforce_totals")
    euro_unit = fields.Float('€ ud', compute="compute_workforce_totals")
    total = fields.Float('€ Total', compute="compute_workforce_totals")


    @api.onchange('printer_id')
    def compute_workforce_totals(self):
        for wcl in self:
            sh = wcl.fdm_sheet_id or wcl.sls_sheet_id or wcl.pol_sheet_id or \
                    wcl.sla_sheet_id or wcl.dmls_sheet_id
            hours_tech = sh.group_id.tech_hours
            if sh.cus_units:
                wcl.euro_unit = wcl.hours * hours_tech / sh.cus_units
            wcl.minutes = wcl.euro_unit * sh.cus_units
            wcl.total = wcl.euro_unit * sh.cus_units



# Coste externalizacion por piezaS
class OutsorcingCostLine(models.Model):

    _name = 'outsorcing.cost.line'

    fdm_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    sls_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    pol_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    sla_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')
    dmls_sheet_id = fields.Many2one('cost.sheet', 'Hoja de coste')

    name = fields.Char('Tarea')
    cost = fields.Float('Coste')
    margin = fields.Float('Margen', default=20.0)
    pvp = fields.Float('PVP ud', compute="_get_pvp")

    @api.depends('cost', 'margin')
    def _get_pvp(self):
        for ocl in self:
            ocl.pvp = ocl.cost * (1 + ocl.margin / 100.0)






    