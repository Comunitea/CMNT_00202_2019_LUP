# © 2020 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields,_, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

letter = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}


class StockLocation(models.Model):

    _inherit = "stock.location"

    loc_format = fields.Selection([('1', 'Pasillo'), ('2', 'Estantería'), ('3', 'Palet'), ('4', 'Armario')], string="Formato de ubicación")
    route_dir = fields.Boolean('Prioridad +/-', help="Si está marcado, la prioridad es positiva en las sububicaciones")

    def get_putaway_strategy(self, product):
        ## Ralentiza muchisimo el action assign
        ## Si la ubicación del movimiento tiene un estrategía, entonces
        domain = [('product_id', '=', product.id), ('putaway_id', '=', self.putaway_strategy_id.id)]
        p_id = self.env['stock.fixed.putaway.strat'].search(domain, limit=1)
        if p_id:
            return p_id.fixed_location_id
        return super().get_putaway_strategy(product)

    def name_get(self):
        ret_list = []
        for location in self:
            if location.loc_format == '4' and location.usage != 'view':
                parent_location = location.location_id.location_id
                if not parent_location:
                    raise UserError(_('You have to set a parent location for this box (%s).'% location.location_id.name))
                name = "%s - %s" % (parent_location.name, location.name)
                ret_list.append((location.id, name))
            elif location.loc_format in ['2', '3']:
                name = location.name
                ret_list.append((location.id, name))
            else:
                orig_location = location
                name = location.name
                while location.location_id and location.usage != 'view' and not location.loc_format:
                    location = location.location_id
                    if not name:
                        raise UserError(_('You have to set a name for this location.'))
                    name = location.name + "/" + name
                ret_list.append((orig_location.id, name))
        return ret_list


    def create_xml_id(self, id, name):
        model = 'stock.location'
        module_name = 'stock_location'
        xml_id = name
        self._cr.execute(
            'INSERT INTO ir_model_data (module, name, res_id, model) \
            VALUES (%s, %s, %s, %s)',
                        (module_name, xml_id, id, model))
    
    @api.multi
    def generar_estanterias(self):
        
        letter = 'ABCDEFGH'
        letter_key = {}
        cont = 1
        letters = []
        letters += "_"
        for a in letter:
            letters += a
            letter_key [a] = cont
            cont +=1
        
        for loc_id in self:
            removal_priority = loc_id.location_id.removal_priority
            usage = 'internal'
            ## Según compañias ?? 
            lup = loc_id.company_id.id == 1
            if loc_id.usage != 'view':
                raise UserError("Solo tipo vista")
            tipo = loc_id.loc_format
            if tipo == '1':
                tipo == '4'

            posx = loc_id.posx
            posy_max = loc_id.posy
            posz_max = loc_id.posz
            rute_dir = loc_id.route_dir
            name = loc_id.name
            for _posy in range(0, posy_max):
                for _posz in range(0, posz_max):
                    posy = _posy +1
                    posz = _posz +1
                   
                    if tipo in ['1','2'] : ## pasillo/estantería
                        loc_name = loc_id.name.upper().replace('D', '1').replace('E','2').replace('A','0') ## 1D es 11, 1E es 10
                        posx = '%02d'%int(loc_name)
                        ## Esto es una mierda pero tienen distintas los nobres de lupeon y dativic
                        if lup:
                            name = '%s-%02d-%02d'%(loc_id.name, posy, posz)
                        else:
                            name = '%s-%02d-%d'%(loc_id.name, posy, posz)
                        rp = posy if rute_dir else 100-posy                    
                        removal_priority = loc_id.removal_priority * 100 + int(rp)
                        
                    elif tipo == '4': ## armario
                        loc_name = loc_id.name.upper().replace('BOX ', 'B')
                        name = '%s-%s-%02d'%(loc_name, letters[posy], posz)
                        tipo = '4'
                    elif tipo == '3': ## Palet
                        loc_name = loc_id.name.upper().replace('PALET ', 'P')
                        name = '%s-%s-%02d'%(loc_name, letters[posy], posz)

                    _logger.info ("Evaluando %s" % name)
                    ##Elimino espacioes en blanco y guion bajo de los códigos de barras
                    barcode = name.replace(' ', '.').replace('_', '-').upper()
                    ##Elimino espacioes en blanco y guion medio para el external_id
                    external_id = name.replace('-', '_').replace(' ', '_').replace('.','_').lower()

                    
                    domain =  [('model', '=', 'stock.location'), ('name', '=', external_id)]
                    new_loc_id = self.env['ir.model.data'].search(domain, limit = 1)
                    if new_loc_id:
                        new_loc_id = self.browse(new_loc_id.res_id)
                        ## Solo actualizo 
                        """
                        vals = {
                            'name': name,
                            'removal_priority': removal_priority,
                            'barcode': barcode}
                        if False:
                            new_loc_id.write(vals)
                            """
                        _logger.info ("->Actualizo %s"%name)

                    else:
                        vals = {
                            'location_id': loc_id.id,
                            'loc_format': tipo, ## '2', ## loc_id.loc_format
                            'usage': usage,
                            'name': name,
                            'barcode': barcode,
                            'posx': posx,
                            'posy': posy,
                            'posz': posz,
                            'removal_priority': removal_priority
                        }
                        new_loc_id = self.create(vals)
                        self.create_xml_id(new_loc_id.id, external_id)
                        _logger.info ("->Creo %s"%name)
                    


