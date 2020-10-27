
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class RegistergroupWizard(models.TransientModel):
    _name = 'register.group.wizard'

    @api.model
    def default_get(self, default_fields):
        gp = self.env['group.production'].browse(
            self._context.get('active_id'))
        res = super().default_get(default_fields)

        res['consume_ids'] = []
        res['qty_done_ids'] = []

        # Load qty
        # for wo in gp.workorder_ids:
        for reg in gp.register_ids:
            wo = reg.workorder_id
            vals = {
                'workorder_id': wo.id,
                'production_id': wo.production_id.id,
                'product_id': wo.product_id.id,
                'product_qty': wo.qty_production,
                'qty_produced': wo.qty_produced,
                # 'qty_done': wo.planned_qty if wo.planned_qty else
                'qty_done': reg.qty_done,
            }
            res['qty_done_ids'].append((0, 0, vals))

        # Load consumes
        for line in gp.material_ids:
            vals = {
                'group_line_id': line.id,
                'product_id': line.product_id.id,
                'qty_consume': line.qty - line.real_qty,
                'lot_id': False,
                'qty_done': 0,
            }
            res['consume_ids'].append((0, 0, vals))
        return res

    machine_hours = fields.Float('Horas máquina')
    user_hours = fields.Float('Horas técnico')
    qty_done_ids = fields.One2many(
        'group.done.line', 'wzd_id', 'Cantidades Producidas')
    consume_ids = fields.One2many(
        'group.consume.line', 'wzd_id', 'Consumos')

    def confirm(self):
        gp = self.env['group.production'].browse(
            self._context.get('active_id'))

        if not self.machine_hours:
            raise UserError('Es necesario indicar el tiempo máquina')

        if not self.user_hours:
            raise UserError('Es necesario indicar las horas de usuario')

        for consume in self.consume_ids:
            if not consume.lot_id:
                raise UserError('Es necesario indicar lote \
                        para el producto %s' % consume.product_id.name)
            if not consume.qty_done:
                raise UserError('Es necesario indicar na cantidad consumida \
                    para el producto %s' % consume.product_id.name)

        total_user_hours = 0
        total_machine_hours = 0
        total_gr = 0
        for line in self.qty_done_ids:

            wo = line.workorder_id
            if not wo or wo.state not in ('ready', 'progress'):
                continue
            h_ud = wo.th_user_hours / line.product_qty
            h_qty = h_ud * line.qty_done
            total_user_hours += h_qty

            h_ud = wo.th_machine_hours / line.product_qty
            h_qty = h_ud * line.qty_done
            total_machine_hours += h_qty

            for move in line.mapped('workorder_id.active_move_line_ids'):
                if line.product_qty:
                    qty_gr_unit = move.qty_done / move.production_id.product_qty
                    done_qty = line.qty_done * qty_gr_unit
                    total_gr += done_qty

        for line in self.qty_done_ids:

            if not line.qty_done:
                raise UserError('Es necesario indicar la cantidad prducida \
                    para el producto %s' % line.product_id.name)

            wo = line.workorder_id
            if not wo or wo.state not in ('ready', 'progress'):
                continue

            wo.button_start()
            if wo.time_ids and line.product_qty and total_user_hours:
                h_ud = wo.th_user_hours / line.product_qty
                h_qty = h_ud * line.qty_done
                percent = h_qty / total_user_hours
                h = self.user_hours * percent
                t = wo.time_ids.filtered(lambda x: not x.date_end)
                next_date = t.date_start + timedelta(hours=h)
                # wo.time_ids[0].duration = self.total_time * 60 * percent
                wo.time_ids[0].date_end = next_date

            consume_ids = []
            for move in wo.active_move_line_ids:

                # Reparto proporcional consumos
                grouped_line = self.consume_ids.filtered(
                    lambda x: x.product_id == move.product_id)
                prop_qty = 0
                if total_gr and line.product_qty:
                    qty_gr_unit = move.qty_done / line.product_qty
                    done_qty = line.qty_done * qty_gr_unit
                    percent = done_qty / total_gr
                    prop_qty = grouped_line.qty_done * percent

                consume_vals = {
                    'product_id': line.product_id.id,
                    'lot_id': grouped_line.lot_id.id,
                    'qty_done': prop_qty,
                    'move_line_id': move.id,
                }
                consume_ids.append((0, 0, consume_vals))

            if line.product_qty and total_machine_hours:
                h_ud = wo.th_machine_hours / line.product_qty
                h_qty = h_ud * line.qty_done
                percent = h_qty / total_machine_hours
                h = self.machine_hours * percent
                vals = {
                    'qty': line.qty_done,
                    'machine_hours': h,
                    'consume_ids': consume_ids
                }
                reg = self.env['register.workorder.wizard'].with_context(
                    active_id=wo.id).new(vals)
                reg.confirm()

        gp.state = 'done'

        if self.machine_hours:
            time = gp.total_time
            gp.total_time = time + self.machine_hours

        # Actualizo consumos
        for consume in self.consume_ids:
            consume.group_line_id.write({
                'real_qty':
                consume.group_line_id.real_qty + consume.qty_done})

        # Vuelvo a dejar la cantidad planificada a 0
        # gp.workorder_ids.write({'planned_qty': 0})
        return


class GroupConsumeLine(models.TransientModel):
    _name = 'group.done.line'

    wzd_id = fields.Many2one(
        'register.group.wizard', 'Registro producción')
    workorder_id = fields.Many2one(
        'mrp.workorder', 'Orden de trabajo', readonly=True)
    production_id = fields.Many2one(
        'mrp.production', 'Producción Asociada', readonly=True)
    product_id = fields.Many2one(
        'product.product', 'Producto', readonly=True)
    product_qty = fields.Float(
        'Cantidad inicial', readonly=True)
    qty_produced = fields.Float(
        'Cantidad producida', readonly=True)
    qty_done = fields.Float('Cantidad realizada')


class ConsumeLine(models.TransientModel):
    _name = 'group.consume.line'

    wzd_id = fields.Many2one(
        'register.group.wizard', 'Registro producción')
    group_line_id = fields.Many2one(
        'group.material.line', 'Movimiento agrupado', readonly=True)
    product_id = fields.Many2one(
        'product.product', 'Producto', readonly=True)
    qty_consume = fields.Float(
        'Cantidad a consumir', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lote', required=True)
    qty_done = fields.Float('Cantidad consumida', required=True)