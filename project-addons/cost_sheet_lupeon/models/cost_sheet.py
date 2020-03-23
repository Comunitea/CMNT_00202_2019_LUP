# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _

SHEET_TYPES = [
    ('design', 'Design'),
    ('fdm', 'FDM'),
    ('sls', 'SLS'),
    ('sla', 'SLA'),
    ('dmls', 'DMLS'),
    ('oppi', 'OPPI'),
]

class CostSheet(models.Model):

    _name = 'cost.sheet'

    name = fields.Char('Name')

    sheet_type = fields.Selection(SHEET_TYPES, 'Sheet Type')

    init_cost = fields.Float('Init Cost')
    admin_fact = fields.Float('Administrative factor')
    disc_qty = fields.Float('Discount quantity')
    disc2 = fields.Float('Additional discount')
    increment = fields.Float('Increment')
    inspection_type = fields.Selection(
        [('visual', 'Visual'), ('tech', 'Technical')])

    # COMUN
    product_id = fields.Many2one('product.product', 'Design Reference')

    # DISEÑO
    flat_ref = fields.Char('Flat ref')
    legislation_ids = fields.Many2many(
        'applicable.legislation',
        'cost_sheet_applicable_legislation_rel',
        'sheet_id', 'legislation_id',
        string='Applicable legislation')
    time_line_ids = fields.One2many('design.time.line', 'sheet_id', string='Times')
    description = fields.Text('Technical Requisist')
    customer_note = fields.Text('Customer Coments')
    hours_total = fields.Float('Hours total', compute="_get_totals")
    amount_total = fields.Float('Amount total', compute="_get_totals")

    # ------------------------------------------------------------------------

    # FDM DATOS PIEZA
    fdm_units = fields.Integer('Uds. Customer')
    cc_und = fields.Integer('CC UD')
    euros_cc = fields.Float('€ / CC')
    stat_data = fields.Char('Statics Data')
    
    # FDM PARÁMETROS IMPRESIÓN
    printer_id = fields.Many2one(
        'printer.machine', 'Printer', domain=[('type', '=', 'fdm')])
    tray_units = fields.Integer('Tray Units')
    infill = fields.Float('Infill')  # Model or selection?
    loops = fields.Integer('Loops') # Model or selection?
    layer_height = fields.Float('Layer Height') # Model or selection?
    tray_hours = fields.Float('Tray Hours')
    euro_machine = fields.Float('€ / Machine')
    perfil = fields.Char('Perfil')

    # FDM COSTE MATERIAL
    material_cost_ids = fields.One2many(
        'material.cost.line', 'fdm_sheet_id', string='Cost Material')
    total_euro_ud = fields.Float('Total € Ud.')
    total_material_cost = fields.Float('Total')
    
    # FDM COSTE MÁQUINA
    machine_hours = fields.Float('Total Machine Hours')
    euro_machine_ud = fields.Float('€ / Machine uf')  
    euro_machine_total = fields.Float('Total Machine')
    # FDM COSTE MANO DE OBRA
    workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'fdm_sheet_id', string='Cost Material')
    
    # FDM COSTE EXTERNALIZACION POR PIEZA
    outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'fdm_sheet_id', string='Outsorcing Cost')
    outsorcing_total_ud = fields.Float(
        'Total ud.l', compute="_get_totals_outsorcing")
    outsorcing_total = fields.Float(
    'Total ud.l', compute="_get_totals_outsorcing")

    # FDM PART FEATURES
    feature_ids = fields.Many2many(
        'part.feature',
        'cost_sheet_paer_features_rel',
        'sheet_id', 'feature_id',
        string='Part Features')
    
    # ------------------------------------------------------------------------
    
    # SLS DATOS PIEZA
    units_sls = fields.Integer('Uds. Customer')
    cc_und_sls = fields.Integer('CC UD')
    cm2_sls = fields.Float('cm2 ud')
    x_mm_sls = fields.Float('X (mm)')
    y_mm_sls = fields.Float('Y (mm)')
    z_mm_sls = fields.Float('Z (mm)')
    static_data_sls = fields.Char('Static data')
    e_cc_sls = fields.Float('€/cc')

    # SLS PARÁMETROS IMPRESIÓN
    sls_printer_id = fields.Many2one(
        'printer.machine', 'Printer', domain=[('type', '=', 'sla')])
    tray_units_sls = fields.Integer('Tray Units')
    increment_sls = fields.Float('Increment')  # Model or selection?
  
    tray_hours_sls = fields.Float('Tray Hours')
    euro_machine_sls = fields.Float('€ / Machine')

    # SLS OFERT CONFIGURATION
    offer_type = fields.Selection(
        [('standard', 'Standard'),
         ('xyz', 'XYZ'),
         ('cubeta', 'Cubeta')], 'Offer type')
    solid_per_sls = fields.Float('Solid percent')
    bucket_height_sls = fields.Float('Bucket Height')
    simulation_time_sls = fields.Float('Simulation time')

    # SLS MATERIAL COST
    sls_material_cost_ids = fields.One2many(
        'material.cost.line', 'sls_sheet_id', string='Cost Material')

    # SLS COSTE MÁQUINA
    machine_hours_sls = fields.Float('Total Machine Hours')
    euro_machine_ud_sls = fields.Float('€ / Machine ud')  
    euro_machine_total_sls = fields.Float('Total Machine')

    # SLS COSTE MANO DE OBRA
    sls_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sls_sheet_id', string='Cost Material')
    
    # SLS COSTE EXTERNALIZACION POR PIEZA
    sls_outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'sls_sheet_id', string='Outsorcing Cost')
    outsorcing_total_ud_sls = fields.Float(
        'Total ud.l', compute="_get_totals_outsorcing_sls")
    outsorcing_total_sls = fields.Float(
    'Total ud.l', compute="_get_totals_outsorcing_sls")
    tinted_sls = fields.Selection(
        [('blue', 'Blue'),
         ('black', 'XYZ'),
         ('no_tinted', 'No tinted'),
         ('other', 'Other colors')], 'Tinted')

    # ------------------------------------------------------------------------ 

    # POLY DATOS PIEZA
    units_pol = fields.Integer('Uds. Customer')
    cc_und_pol = fields.Integer('CC UD')
    stat_data_pol = fields.Char('Statics Data')
    euros_cc_pol = fields.Float('€ / CC')

    # POLY PARÁMETROS IMPRESIÓN
    pol_printer_id = fields.Many2one(
        'printer.machine', 'Printer', domain=[('type', '=', 'poly')])
    tray_units_pol = fields.Integer('Tray Units')
    finish_pol = fields.Selection([
        ('glossy', 'Glossy'),
        ('mate', 'Mate')], 'Tinted')
    tray_hours_pol = fields.Float('Tray Hours')
    euro_machine_pol = fields.Float('€ / Machine')

    # POLY MATERIAL COST
    pol_material_cost_ids = fields.One2many(
        'material.cost.line', 'pol_sheet_id', string='Cost Material')

    # POLY COSTE MÁQUINA
    machine_hours_pol = fields.Float('Total Machine Hours')
    euro_machine_ud_pol = fields.Float('€ / Machine ud')  
    euro_machine_total_pol = fields.Float('Total Machine')

    # POLY COSTE MANO DE OBRA
    pol_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'pol_sheet_id', string='Cost Material')

    # POLY COSTE EXTERNALIZACION POR PIEZA
    pol_outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'pol_sheet_id', string='Outsorcing Cost')
    outsorcing_total_ud_pol = fields.Float(
        'Total ud.l', compute="_get_totals_outsorcing_sls")
    outsorcing_total_pol = fields.Float(
    'Total ud.l', compute="_get_totals_outsorcing_sls")

    # ------------------------------------------------------------------------- 

    # SLA DATOS PIEZA
    units_sla = fields.Integer('Uds. Customer')
    cc_und_sla = fields.Integer('CC UD')
    stat_data_sla = fields.Char('Statics Data')
    euros_cc_sla = fields.Float('€ / CC')

    # SLA PARÁMETROS IMPRESIÓN
    sla_printer_id = fields.Many2one(
        'printer.machine', 'Printer', domain=[('type', '=', 'sla')])
    tray_units_sla = fields.Integer('Tray Units')
    tray_hours_sla = fields.Float('Tray Hours')
    euro_machine_sla = fields.Float('€ / Machine')

    # SLA MATERIAL COST
    sla_material_cost_ids = fields.One2many(
        'material.cost.line', 'sla_sheet_id', string='Cost Material')

    # SLA COSTE MÁQUINA
    machine_hours_sla = fields.Float('Total Machine Hours')
    euro_machine_ud_sla = fields.Float('€ / Machine ud')  
    euro_machine_total_sla = fields.Float('Total Machine')

    # SLA COSTE EXTERNALIZACION POR PIEZA
    sla_outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'sla_sheet_id', string='Outsorcing Cost')
    outsorcing_total_ud_sla = fields.Float(
        'Total ud.l', compute="_get_totals_outsorcing_sls")
    outsorcing_total_sla = fields.Float(
    'Total ud.l', compute="_get_totals_outsorcing_sls")

    # SLA COSTE MANO DE OBRA
    sla_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sla_sheet_id', string='Cost Material')
    
    # ------------------------------------------------------------------------- 

    # DMLS DATOS PIEZA
    units_dmls = fields.Integer('Uds. Customer')
    cc_und_dmls = fields.Integer('CC UD')
    cc_soport = fields.Integer('CC soport')
    stat_data_dmls = fields.Char('Statics Data')
    euros_cc_dmls = fields.Float('€ / CC')

    # SLA PARÁMETROS IMPRESIÓN
    dmls_printer_id = fields.Many2one(
        'printer.machine', 'Printer', domain=[('type', '=', 'dmls')])
    tray_units_dmls = fields.Integer('Tray Units')
    tray_hours_dmls = fields.Float('Tray Hours')
    euro_machine_dmls = fields.Float('€ / Machine')

    # SLA MATERIAL COST
    dmls_material_cost_ids = fields.One2many(
        'material.cost.line', 'sla_sheet_id', string='Cost Material')

    # SLA COSTE MÁQUINA
    machine_hours_dmls = fields.Float('Total Machine Hours')
    euro_machine_ud_dmls = fields.Float('€ / Machine ud')  
    euro_machine_total_dmls = fields.Float('Total Machine')

    # SLA COSTE EXTERNALIZACION POR PIEZA
    dmls_outsorcing_cost_ids = fields.One2many(
        'outsorcing.cost.line', 'sla_sheet_id', string='Outsorcing Cost')
    outsorcing_total_ud_dmls = fields.Float(
        'Total ud.l', compute="_get_totals_outsorcing_sls")
    outsorcing_total_dmls = fields.Float(
    'Total ud.l', compute="_get_totals_outsorcing_sls")

    # SLA COSTE MANO DE OBRA
    dmls_workforce_cost_ids = fields.One2many(
        'workforce.cost.line', 'sla_sheet_id', string='Cost Material')

    @api.depends('time_line_ids')
    def _get_totals(self):
        for sh in self:
            sh.hours_total = sum([x.hours for x in sh.time_line_ids])
            sh.amount_total = sum([x.total for x in sh.time_line_ids])

    @api.depends('outsorcing_cost_ids')
    def _get_totals_outsorcing(self):
        for sh in self:
            sh.outsorcing_total_ud = sum([x.pvp for x in sh.outsorcing_cost_ids])
            sh.outsorcing_total =sh.outsorcing_total_ud * sh.fdm_units

    @api.depends('sls_outsorcing_cost_ids')
    def _get_totals_outsorcing_sls(self):
        for sh in self:
            sh.outsorcing_total_ud_sls = sum([x.pvp for x in sh.sls_outsorcing_cost_ids])
            sh.outsorcing_total_sls =sh.outsorcing_total_ud_sls * sh.fdm_units


class DesignTimeLine(models.Model):

    _name = 'design.time.line'

    sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    software_id = fields.Many2one('design.software', 'Design Software')
    hours = fields.Float('Hours')
    price_hour = fields.Float('Price Hour')
    discount = fields.Float('Discount')
    total = fields.Float('Total', compute="_compute_total")

    @api.depends('hours', 'price_hour', 'discount')
    def _compute_total(self):
        for line in self:
            line.total = \
                line.hours * line.price_hour * (1 - line.discount / 100.0)
    
    @api.onchange('software_id')
    def _compute_total(self):
        for line in self:
            line.price_hour = line.software_id.price_hour

# FDM COSTE MATERIAL
class MaterialCostLine(models.Model):

    _name = 'material.cost.line'

    # COMUN
    name = fields.Char('Name')
    material_id = fields.Many2one('material', 'Material')
    euro_material = fields.Float('€ Material')
    gr_tray = fields.Float('Gr tray')
    gr_total = fields.Float('Gr total')
    total = fields.Float('Total')

    # FDM
    fdm_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    diameter = fields.Float('Diameter')
    color = fields.Char('Color')
    tray_meters = fields.Char('Tray Meters')
    gr_cc_tray = fields.Float('Gr cc / Tray')
    gr_cc_total = fields.Float('Gr cc total')

    # SLS
    sls_sheet_id = fields.Many2one('cost.sheet', 'Sheet')

    # POLY
    pol_sheet_id = fields.Many2one('cost.sheet', 'Sheet')

    # SLA
    sla_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    desviation = fields.Float('Desviation material')
    cc_tray = fields.Float('Gr cc / Tray')
    cc_total = fields.Float('Total')

    # DMLS
    dmls_sheet_id = fields.Many2one('cost.sheet', 'Sheet')





# FDM COSTE MANO DE OBRA
class WorkforceCostLine(models.Model):

    _name = 'workforce.cost.line'

    fdm_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    sls_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    pol_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    sla_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    dmls_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    name = fields.Char('Name')
    minutes = fields.Float('Diameter')
    euro_unit = fields.Float('Gr cc / Tray')
    total = fields.Float('Gr cc / Tray')


# OUTSORCING COSTS
class OutsorcingCostLine(models.Model):

    _name = 'outsorcing.cost.line'

    fdm_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    sls_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    pol_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    sla_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    dmls_sheet_id = fields.Many2one('cost.sheet', 'Sheet')
    name = fields.Char('Task')
    cost = fields.Float('Cost')
    margin = fields.Float('Margin')
    pvp = fields.Float('PvP')






    