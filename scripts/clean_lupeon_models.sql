-- Limpiado de lupeon
delete from sale_order where company_id = 1;
delete from stock_picking where company_id = 1;
delete from stock_move where company_id = 1;
delete from stock_quant where company_id = 1;


delete from stock_move_line where picking_id is null;

delete from stock_move_line where id in (
    select sml.id from stock_move_line sml
    inner join stock_move sm on sml.move_id = sm.id where sml.picking_id is null and sm.company_id = 1);


delete from project_project pp where company_id = 1;
delete from project_task where company_id = 1;
delete from change_production_qty;

delete from mrp_production where company_id = 1;
delete from mrp_workorder;
delete from group_cost_sheet where sale_line_id is null;
delete from cost_sheet where sale_line_id is null;
delete from purchase_order where company_id = 1;
delete from group_production;
delete from mrp_routing where created_on_fly is true;
delete from mrp_bom where company_id = 1;
-- otras
-- update product_template set tracking='lot' where is_material is True;
