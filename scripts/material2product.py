# -*- coding: utf-8 -*-
db_name = 'LUPEON'
session.open(db=db_name)
print("******************START************************")
materials = session.env['material'].search([])
tot = len(materials)
i = 0
for mat in materials:
    i += 1
    print('%s/%s' % (i, tot))
    vals = {
        'name': mat.name,
        'is_material': True,
        'gr_cc': mat.gr_cc,
        'euro_kg': mat.euro_kg,
        'factor_hour': mat.factor_hour,
        'dens_cc': mat.dens_cc,
        'dens_bulk': mat.dens_bulk,
        'vel_cc': mat.vel_cc,
        'vel_z': mat.vel_z,
        'euro_kg_bucket': mat.euro_kg_bucket,
        'euro_hour_maq': mat.euro_hour_maq,
        'euro_cc': mat.euro_cc,
        'printer_id': mat.printer_id and mat.printer_id.id,
        'washing_time': mat.washing_time,
        'cured_time': mat.cured_time,
        'init_cost': mat.init_cost,
    }
    session.env['product.product'].create(vals)
print("******** **********DONE************************")
session.cr.commit()