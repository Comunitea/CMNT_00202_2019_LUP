# © 2020 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.tools.view_validation import valid_view

from lxml import etree

_logger = logging.getLogger(__name__)

class View(models.Model):

    _inherit = "ir.ui.view"

    num_line = fields.Char(string='Nº Line')

    @api.constrains('arch_db')
    def _check_xml(self):
        """
        SOBREESCRIBO PARA SALTARME UNA VISTA EN CONCRETO
        TODO SE PUEDE HACER HEREDANDO SIN PISAR
        """
        # Sanity checks: the view should not break anything upon rendering!
        # Any exception raised below will cause a transaction rollback.
        self = self.with_context(check_field_names=True)
        for view in self:
            if view.name=="skip.check.in.purchase.product.custom.tree":
                continue    
            view_arch = etree.fromstring(view.arch.encode('utf-8'))
            view._valid_inheritance(view_arch)
            view_def = view.read_combined(['arch'])
            view_arch_utf8 = view_def['arch']
            if view.type != 'qweb':
                view_doc = etree.fromstring(view_arch_utf8)
                self._check_groups_validity(view_doc, view.name)
                # verify that all fields used are valid, etc.
                self.postprocess_and_fields(view.model, view_doc, view.id)
                # RNG-based validation is not possible anymore with 7.0 forms
                view_docs = [view_doc]
                if view_docs[0].tag == 'data':
                    # A <data> element is a wrapper for multiple root nodes
                    view_docs = view_docs[0]
                for view_arch in view_docs:
                    check = valid_view(view_arch)
                    if not check:
                        raise ValidationError(_('Invalid view %s definition in %s') % (view.name, view.arch_fs))
                    if check == "Warning":
                        _logger.warning(_('Invalid view %s definition in %s \n%s'), view.name, view.arch_fs, view.arch)
        return True