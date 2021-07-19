# -*- coding: utf-8 -*-
db_name = 'prod_LUPEON_09_07'
session.open(db=db_name)
print("******************START************************")
ams = session.env['account.move'].search([('journal_id', '=', 10)])
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
for move in ams:
    print(i)
    # for line in am.line_ids:
    #     print(line.name)
    #     print(line.account_id.code.find('477'))
    #     print(line.name.find('IVA 21'))
    
        
        
    #COMPRAS INTRACOMUNITARIAS 
    compras_21_ic = move.line_ids.filtered(lambda l: TAXES['c_ic_21'] in l.tax_ids.ids and TAXES['c_ic_21_472'] not in l.tax_ids.ids) # tienen el padre pero no hijos
    if compras_21_ic:
        print("FACTURA INTRAC")
        debe = sum(compras_21_ic.mapped('debit'))
        haber = sum(compras_21_ic.mapped('credit'))
        if debe > 0:
            debit = debe * 0.21
            credit = 0
        if haber > 0:
            print ("ABONO")

            debit = 0 
            credit = haber * 0.21


        ml_1 = session.env['account.move.line'].create(
                {
                'account_id': 860,  #472
                'debit': debit ,
                'credit': credit,
                'name': 'IVA 21% Intracomunitario. Bienes corrientes (1)',
                'partner_id': compras_21_ic[0].partner_id.id,
                'tax_line_id': TAXES['c_ic_21_472'],
                'move_id': move.id
                }
            )
        ml_2 = session.env['account.move.line'].create(
        {
            'account_id': 871,  #477
            'debit': credit ,
            'credit': debit,
            'name': 'IVA 21% Intracomunitario. Bienes corrientes (2)',
            'partner_id': compras_21_ic[0].partner_id.id,
            'tax_line_id': TAXES['c_ic_21_477'],
            'move_id': move.id
        }
        )
        compras_21_ic.write({'tax_ids': [(6, 0, (TAXES['c_ic_21'], TAXES['c_ic_21_472'], TAXES['c_ic_21_477'] ))]})
       
    #COMPRAS SERVCIOS INTRACOMUNITARIOS 
    compras_s_21_ic = move.line_ids.filtered(lambda l: TAXES['c_ic_s_21'] in l.tax_ids.ids and TAXES['c_ic_s_21_472'] not in l.tax_ids.ids) # tienen el padre pero no hijos
  
    if compras_s_21_ic:
        print("FACTURA SERV INTRAC")
        debe = sum(compras_s_21_ic.mapped('debit'))
        haber = sum(compras_s_21_ic.mapped('credit'))
        if debe > 0:
            debit = debe * 0.21
            credit = 0
        if haber > 0:
            print ("ABONO")
            debit = 0 
            credit = haber * 0.21
        session.env['account.move.line'].create(
            {
            'account_id': 860,  #472
            'debit': debit ,
            'credit': credit,
            'name': 'IVA 21% Inversión del sujeto pasivo intracomunitario (1)',
            'partner_id': compras_s_21_ic[0].partner_id.id,
            'tax_line_id': TAXES['c_ic_s_21_472'],
            'move_id': move.id
            }
        )
        session.env['account.move.line'].create(
        {
            'account_id': 871,  #477
            'debit': credit ,
            'credit': debit,
            'name': 'IVA 21% Inversión del sujeto pasivo intracomunitario (2)',
            'partner_id': compras_s_21_ic[0].partner_id.id,
            'tax_line_id': TAXES['c_ic_s_21_477'],
            'move_id': move.id
        }
        )
        compras_s_21_ic.write({'tax_ids': [(6, 0, (TAXES['c_ic_s_21'], TAXES['c_ic_s_21_472'], TAXES['c_ic_s_21_477'] ))]})
  
        
    
    print(move.id)
    i=i+1

session.cr.commit()