
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RegisterWorkorderWizard(models.TransientModel):
    _name = 'register.workorder.wizard'
    _description = "Register Workorder Wizard"

    @api.model
    def default_get(self, default_fields):
        wo = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        res = super().default_get(default_fields)
        res['qty'] = 0
        res['consume_ids'] = []
        for move in wo.active_move_line_ids:
            vals = {
                'product_id': move.product_id.id,
                'lot_id': move.lot_id.id,
                'qty_done': 0,
                'move_line_id': move.id,
            }
            res['consume_ids'].append((0, 0, vals))
        return res

    qty = fields.Float('Cantidad hecha', required=True)
    machine_hours = fields.Float('Horas máquina')
    consume_ids = fields.One2many('consume.line', 'wzd_id', 'Consumos')

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

    def confirm(self):
        wo = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        wo.button_pending()
        wo.qty_producing = self.qty

        if self.consume_ids and not self.machine_hours:
            raise UserError('Es necesario indicar el tiempo máquina')

        vals = {
            'workorder_id': wo.id,
            'time': self.machine_hours
        }
        self.env['machine.time'].create(vals)

        # Escribo las horas máquina
        mh = self.printer_instance_id.machine_hours
        self.printer_instance_id.machine_hours = mh + self.machine_hours

        wo.production_id.write({
            'printer_instance_id': self.printer_instance_id.id
        })

        # Write consumes on workorrder
        for line in self.consume_ids:
            # line.move_line_id.with_context(bypass_reservation_update=True).write({
            line.move_line_id.write({
                # 'product_id': line.product_id.id,
                'lot_id': line.lot_id.id,
                'qty_done': line.qty_done,
            })
        wo.record_production()
        return


class ConsumeLine(models.TransientModel):
    _name = 'consume.line'
    _description = "Consume Line"

    wzd_id = fields.Many2one(
        'register.workorder.wizard', 'Registro producción')
    move_line_id = fields.Many2one('stock.move.line', 'Movimiento asociado')
    product_id = fields.Many2one('product.product', 'Producto')
    lot_id = fields.Many2one('stock.production.lot', 'Lote')
    qty_done = fields.Float('Cantidad consumida')
