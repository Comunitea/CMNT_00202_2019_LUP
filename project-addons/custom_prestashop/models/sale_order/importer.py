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
                "prestashop.sale.order.line"
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
                            prestashop_binding[item] - float(values[item])
                            > 0.01
                            or prestashop_binding[item] - float(values[item])
                            < -0.01
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
