# -*- coding: utf-8 -*-
from odoo import models,api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    @api.multi
    def get_stock_by_warehouse(self,warehouse_ids):
        headers = {}
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        product_ids = self.ids
        cr = self._cr
        product_inventory_by_wh = {}
        product_inventory_by_location = {}
        for warehouse in self.env['stock.warehouse'].sudo().browse(warehouse_ids):
            headers.update({warehouse.id:'[WH]'+warehouse.code})
            #For faster quantity calculation, used quary.
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations_new([warehouse.lot_stock_id.id])
            domain_quant = [('product_id', 'in', product_ids)] + domain_quant_loc
            query = quant_obj._where_calc(domain_quant)
            from_clause, where_clause, where_clause_params = query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''
            
            from_clause +=', "ir_model_data"'
            where_str +=" AND ((stock_quant.product_id=ir_model_data.res_id) AND (ir_model_data.model='product.product'))"
            query_str = "SELECT CASE WHEN ir_model_data.module!='' THEN concat_ws('.',ir_model_data.module,ir_model_data.name) ELSE ir_model_data.name END as product_ext, sum(quantity) as quantity FROM "+ from_clause + where_str + ' group by product_id, product_ext'
            #query_str = 'SELECT product_id, sum(quantity) as quantity FROM '+ from_clause + where_str + ' group by product_id'
            
            cr.execute(query_str, where_clause_params)
            res = dict(cr.fetchall())
            product_inventory_by_location.update({warehouse.id:res})
        return headers, product_inventory_by_location
        
    @api.multi
    def get_stock_by_locations(self,location_ids):
        headers = {}
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        product_ids = self.ids
        cr = self._cr
        product_inventory_by_wh = {}
        product_inventory_by_location = {}
        for location in self.env['stock.location'].sudo().browse(location_ids):
            headers.update({location.id:'[LOC]'+location.display_name})
            #For faster quantity calculation, used quary.
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations_new([location.id])
            domain_quant = [('product_id', 'in', product_ids)] + domain_quant_loc
            query = quant_obj._where_calc(domain_quant)
            from_clause, where_clause, where_clause_params = query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''
            
            
            from_clause +=', "ir_model_data"'
            where_str +=" AND ((stock_quant.product_id=ir_model_data.res_id) AND (ir_model_data.model='product.product'))"
            query_str = "SELECT CASE WHEN ir_model_data.module!='' THEN concat_ws('.',ir_model_data.module,ir_model_data.name) ELSE ir_model_data.name END as product_ext, sum(quantity) as quantity FROM "+ from_clause + where_str + ' group by product_id, product_ext'
            #query_str = 'SELECT product_id, sum(quantity) as quantity FROM '+ from_clause + where_str + ' group by product_id'
            
            cr.execute(query_str, where_clause_params)
            res = dict(cr.fetchall())
            product_inventory_by_location.update({location.id:res})
            #location_ids.append(location.id)
        return headers, product_inventory_by_location