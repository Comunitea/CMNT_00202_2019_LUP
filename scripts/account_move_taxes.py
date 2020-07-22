# -*- coding: utf-8 -*-
db_name = 'odoo_lupeon_15_07'
session.open(db=db_name)
print("******************START************************")
ams = session.env['account.move'].search([('journal_id', '=', 29)])
tot = len(ams)
i = 0
TAXES = {
    'v_21': 119,
    'v_21_re': 170,
    'c_21': 122,
    'c_10': 159,
    'c_4': 160,
    'c_ic_21': 223,
    'c_ic_21_472': 239,
    'c_ic_21_477': 240,
    'c_ic_s_21': 222,
    'c_ic_s_21_472': 238,
    'c_ic_s_21_477': 237,
    
}
print (tot)
for am in ams:
    print(i)
    # for line in am.line_ids:
    #     print(line.name)
    #     print(line.account_id.code.find('477'))
    #     print(line.name.find('IVA 21'))
    
    #VENTAS NACIONALES al 21%
    ventas_imp_21 = am.line_ids.filtered(lambda line: line.account_id.code.find('477') >=0 and line.name and line.name.find('IVA 21') >=0)
    if ventas_imp_21:
        print("VENTA")
        ventas_imp_21.tax_line_id = TAXES['v_21']
        ventas_21 = am.line_ids.filtered(lambda line: line.account_id.code.find('7') == 0)
        ventas_21.tax_ids = [(4, TAXES['v_21'])]

        ventas_imp_re_21 = am.line_ids.filtered(lambda line: line.account_id.code.find('477') >=0 and line.name and line.name.find('REC 5,2') >=0)
        if ventas_imp_re_21:
            ventas_imp_re_21.tax_line_id = TAXES['v_21_re']
            ventas_21.tax_ids = [(4, TAXES['v_21_re'])]
            
        i = i + 1
        continue                                 
    
    #VENTAS INTRACOMUNITARIAS 
    #ventas_imp_ic = am.line_ids.filtered(lambda line: line.account_id.code.find('477') >=0 and line.name.find('IVA 21') >=0)
    
    
    #COMPRAS NACIONALES al 21%
    compras_imp_21 = am.line_ids.filtered(lambda line: line.account_id.code.find('472') >=0 and line.name and line.name.find('IVA 21') >=0)
    if compras_imp_21:
        print("COMPRA 21")
        compras_imp_21.tax_line_id = TAXES['c_21']
        compras_21 = am.line_ids.filtered(lambda line: line.account_id.code.find('6') == 0)
        compras_21.write({'tax_ids': [(4, TAXES['c_21'])]})
        i = i + 1
        continue
        
        
    #COMPRAS NACIONALES al 10%
    compras_imp_10 = am.line_ids.filtered(lambda line: line.account_id.code.find('472') >=0 and line.name and line.name.find('IVA 10') >=0)
    if compras_imp_10:
        print("COMPRA 10")
        compras_imp_10.tax_line_id = TAXES['c_10']
        compras_10 = am.line_ids.filtered(lambda line: line.account_id.code.find('6') == 0)
        compras_10.write({'tax_ids': [(4, TAXES['c_10'])]})
        i = i + 1
        continue
    
    #COMPRAS NACIONALES al 4%
    compras_imp_4 = am.line_ids.filtered(lambda line: line.account_id.code.find('472') >=0 and line.name and line.name.find('IVA 4') >=0)
    if compras_imp_4:
        print("COMPRA 4")
        compras_imp_4.tax_line_id = TAXES['c_4']
        compras_4 = am.line_ids.filtered(lambda line: line.account_id.code.find('6') == 0)
        compras_4.write({'tax_ids': [(4, TAXES['c_4'])]})
        i = i + 1
        continue
        
        
    #COMPRAS INTRACOMUNITARIAS 
    compras_imp_ic = am.line_ids.filtered(lambda line: line.account_id.code.find('472') >=0 and  line.name and line.name.find('Adq. Intracom. de bienes 21%') >=0)
    if compras_imp_ic:
        print("COMPRA INTRACOMUNITARIA")
        compras_imp_ic.tax_line_id = TAXES['c_ic_21_472']
        compras_imp_ic_477 = am.line_ids.filtered(lambda line: line.account_id.code.find('477') >=0)
        compras_imp_ic_477.tax_line_id = TAXES['c_ic_21_477']
        compras_21_ic = am.line_ids.filtered(lambda line: line.account_id.code.find('6') == 0)
        compras_21_ic.write({'tax_ids': [(6, 0, (TAXES['c_ic_21'], TAXES['c_ic_21_472'], TAXES['c_ic_21_477'] ))]})
        
        i = i + 1
        continue
        
    #COMPRAS SERVCIOS INTRACOMUNITARIOS 
    compras_imp_s_ic = am.line_ids.filtered(lambda line: line.account_id.code.find('472') >=0 and  line.name and line.name.find('Adq. Intracom. de servicios 21%') >=0)
    if compras_imp_s_ic:
        print("COMPRA INTRACOMUNITARIA")
        compras_imp_s_ic.tax_line_id = TAXES['c_ic_s_21_472']
        compras_imp_s_ic_477 = am.line_ids.filtered(lambda line: line.account_id.code.find('477') >=0)
        compras_imp_s_ic_477.tax_line_id = TAXES['c_ic_s_21_477']
        compras_s_21_ic = am.line_ids.filtered(lambda line: line.account_id.code.find('6') == 0)
        compras_s_21_ic.write({'tax_ids': [(6, 0, (TAXES['c_ic_s_21'], TAXES['c_ic_s_21_472'], TAXES['c_ic_s_21_477'] ))]})
        
    print("No localizado")
    print(am.id)
    i=i+1
session.cr.commit()