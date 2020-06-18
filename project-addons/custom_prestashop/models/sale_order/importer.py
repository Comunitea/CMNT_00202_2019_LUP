# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.queue_job.exception import NothingToDoJob


class SaleOrderImporter(Component):
    _inherit = "prestashop.sale.order.importer"

    def _has_to_skip(self):
        """ Sobreescribimos para traernos cualquier actualización sobre el pedido """
        rules = self.component(usage="sale.import.rule")
        try:
            return rules.check(self.prestashop_record)
        except NothingToDoJob as err:
            # we don't let the NothingToDoJob exception let go out, because if
            # we are in a cascaded import, it would stop the whole
            # synchronization and set the whole job to done
            return str(err)


class ImportMapChild(Component):
    _name = "sale.order.line.map.child.import"
    _inherit = "base.map.child.import"

    def format_items(self, items_values):
        """ Format the values of the items mapped from the child Mappers.

        It can be overridden for instance to add the Odoo
        relationships commands ``(6, 0, [IDs])``, ...

        As instance, it can be modified to handle update of existing
        items: check if an 'id' has been defined by
        :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
        command

        :param items_values: list of values for the items to create
        :type items_values: list

        """
        res = []
        for values in items_values:
            if "tax_id" in values:
                values.pop("tax_id")
            prestashop_id = values["prestashop_id"]
            prestashop_binding = self.binder_for(
                self.env.context['model_name']
            ).to_internal(prestashop_id)
            if prestashop_binding:
                values.pop("prestashop_id")
                final_vals = {}
                for item in values.keys():
                    # integer and float values come as string
                    if (
                        prestashop_binding._fields[item].type == "integer"
                        and values[item]
                    ):
                        if int(values[item]) != prestashop_binding[item]:
                            final_vals[item] = values[item]
                    elif (
                        prestashop_binding._fields[item].type == "float"
                        and values[item]
                    ):
                        if float(values[item]) != prestashop_binding[item] and (
                            prestashop_binding[item] - float(values[item]) > 0.01
                            or prestashop_binding[item] - float(values[item]) < -0.01
                        ):
                            final_vals[item] = values[item]
                    elif prestashop_binding._fields[item].type == "many2one":
                        if values[item] != prestashop_binding[item].id:
                            final_vals[item] = values[item]
                    else:
                        if values[item] != prestashop_binding[item]:
                            final_vals[item] = values[item]
                if final_vals:
                    res.append((1, prestashop_binding.id, final_vals))
            else:
                res.append((0, 0, values))
        return res


class SaleOrderImportMapper(Component):
    _inherit = "prestashop.sale.order.mapper"
    _map_child_fallback = "sale.order.line.map.child.import"

    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

    @mapping
    @only_create
    def name(self, record):
        basename = record["reference"]
        if not self._sale_order_exists(basename):
            return {"name": basename}
        i = 1
        name = basename + "_%d" % (i)
        while self._sale_order_exists(name):
            i += 1
            name = basename + "_%d" % (i)
        return {"name": name}

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        context = dict(self.env.context)
        context['model_name'] = model_name
        self.env.context = context
        return super()._map_child(map_record, from_attr, to_attr, model_name)

    @mapping
    def fiscal_position_id(self, record):
        order_lines = record.get('associations').get('order_rows').get('order_row')
        if isinstance(order_lines, dict):
            order_lines = [order_lines]
        line_taxes = []
        sale_line_adapter = self.component(
            usage='backend.adapter',
            model_name='prestashop.sale.order.line'
        )
        for line in order_lines:
            line_data = sale_line_adapter.read(line['id'])
            if line_data.get('associations').get('taxes') and line_data.get('associations').get('taxes').get('tax'):
                prestashop_tax_id = line_data.get('associations').get('taxes').get('tax').get('id')
                if prestashop_tax_id not in line_taxes:
                    line_taxes.append(prestashop_tax_id)
        fiscal_positions = self.env['account.fiscal.position']
        for tax_id in line_taxes:
            matched_fiscal_position = self.env['account.fiscal.position'].search([('prestashop_tax_ids', 'ilike', tax_id)])
            fiscal_positions += matched_fiscal_position.filtered(lambda r: tax_id in r.prestashop_tax_ids.split(','))
        if not fiscal_positions:
            binder = self.binder_for('prestashop.address')
            shipping = binder.to_internal(record['id_address_delivery'], unwrap=True)
            if shipping.country_id in self.env.ref('base.europe').country_ids:
                fiscal_positions = self.env.ref('l10n_es.2_fp_intra')
            else:
                fiscal_positions = self.env['account.fiscal.position'].search([('prestashop_no_taxes', '=', True)])
        if len(fiscal_positions) > 1:
            preferred_fiscal_positions = fiscal_positions.filtered(lambda r: self.backend_record in r.preferred_for_backend_ids)
            if preferred_fiscal_positions:
                fiscal_positions = preferred_fiscal_positions
        if len(fiscal_positions) != 1:
            raise Exception('Error al importar posicion fiscal para los impuestos {}'.format(line_taxes))
        return {'fiscal_position_id': fiscal_positions.id}
        pass

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        binder = self.binder_for('prestashop.sale.order')
        source = map_record.source
        if callable(from_attr):
            child_records = from_attr(self, source)
        else:
            child_records = source[from_attr]
        exists = binder.to_internal(source['id'])
        current_lines = []
        remove_lines = []
        if exists:
            incoming_lines = [int(x['id']) for x in child_records]
            if model_name == 'prestashop.sale.order.line':
                current_lines = [x.prestashop_id for x in exists.prestashop_order_line_ids]
            else:
                current_lines = [x.prestashop_id for x in exists.prestashop_discount_line_ids]
            remove_lines = list(set(current_lines) - set(incoming_lines))
        context = dict(self.env.context)
        context['model_name'] = model_name
        self.env.context = context
        res = super()._map_child(map_record, from_attr, to_attr, model_name)
        if remove_lines:
            for line in remove_lines:
                res.append((2, line))
        return res
