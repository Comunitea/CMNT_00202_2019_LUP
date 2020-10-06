select * from sale_order where company_id = 1 and id!=1520;
select * from sale_order_line where company_id = 1 and order_id!=1520;
select * from stock_picking where company_id = 1;
select * from stock_move where company_id = 1;
select * from stock_move_line where picking_id is null;
select * from project_project pp where company_id = 1;
select * from project_task where company_id = 1;
select * from mrp_production where company_id = 1;
select * from mrp_workorder;
select * from group_cost_sheet where sale_line_id is null;
select * from meet_cost_line;
select * from purchase_order where company_id = 1;

-- Limpiado de lupeon
delete from sale_order where company_id = 1 and id!=1520;
delete from stock_picking where company_id = 1;
delete from stock_move where company_id = 1;
delete from stock_move_line where picking_id is null;
delete from project_project pp where company_id = 1;
delete from project_task where company_id = 1;
delete from change_production_qty;

delete from mrp_production where company_id = 1;
delete from mrp_workorder;
delete from group_cost_sheet where sale_line_id is null;
delete from cost_sheet where sale_line_id is null;
delete from purchase_order where company_id = 1;

-- otras
update product_template set tracking='lot' where is_material is True;
