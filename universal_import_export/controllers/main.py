# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import ExportFormat
from odoo.http import content_disposition, request
from odoo import http
from odoo.tools import misc
import json
import operator

class ImportControllerProduct(http.Controller):

    @http.route('/base_import/set_file_product', methods=['POST'])
    def set_file(self, file, import_id, jsonp='callback'):
        import_id = int(import_id)

        written = request.env['base_import.import.product'].browse(import_id).write({
            'file': file.read(),
            'file_name': file.filename,
            'file_type': file.content_type,
        })

        return 'window.top.%s(%s)' % (misc.html_escape(jsonp), json.dumps({'result': written}))


class ExportFormatProduct(ExportFormat):
    
#     def get_stock_by_locations(self, products,location_ids):
#         headers = {}
#         product_obj = request.env['product.product']
#         quant_obj = request.env['stock.quant']
#         product_ids = products.ids
#         cr = request.cr
#         product_inventory_by_wh = {}
#         product_inventory_by_location = {}
#         for location in request.env['stock.location'].sudo().browse(location_ids):
#             headers.update({location.id :'[LOC]'+location.display_name})
#             #For faster quantity calculation, used quary.
#             domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations_new([location.id])
#             domain_quant = [('product_id', 'in', product_ids)] + domain_quant_loc
#             query = quant_obj._where_calc(domain_quant)
#             from_clause, where_clause, where_clause_params = query.get_sql()
#             where_str = where_clause and (" WHERE %s" % where_clause) or ''
#             
#             
#             from_clause +=', "ir_model_data"'
#             where_str +=" AND ((stock_quant.product_id=ir_model_data.res_id) AND (ir_model_data.model='product.product'))"
#             query_str = "SELECT CASE WHEN ir_model_data.module!='' THEN concat_ws('.',ir_model_data.module,ir_model_data.name) ELSE ir_model_data.name END as product_ext, sum(quantity) as quantity FROM "+ from_clause + where_str + ' group by product_id, product_ext'
#             #query_str = 'SELECT product_id, sum(quantity) as quantity FROM '+ from_clause + where_str + ' group by product_id'
#             
#             cr.execute(query_str, where_clause_params)
#             res = dict(cr.fetchall())
#             product_inventory_by_location.update({location.id:res})
#             #location_ids.append(location.id)
#         return headers, product_inventory_by_location
            
    def base(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)
        
        location_ids = params.get('location_ids')
        warehouse_ids = params.get('warehouse_ids')
         
        Model = request.env[model].with_context(import_compat=import_compat, **params.get('context', {}))
        records = Model.browse(ids) or Model.search(domain, offset=0, limit=False, order=False)

        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']

        field_names = [f['name'] for f in fields]
        import_data = records.export_data(field_names, self.raw_data).get('datas',[])
            
        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]
        if warehouse_ids and records._name=='product.product':
            warehouse_headers, inventory_by_warehouse = records.get_stock_by_warehouse(warehouse_ids)
            for warehouse_id in warehouse_ids:
                columns_headers.append(warehouse_headers.get(warehouse_id))
                
            for data in import_data:
                for warehouse_id in warehouse_ids:
                    data.append(inventory_by_warehouse.get(warehouse_id,{}).get(data[0],0.0))
            
        if location_ids and records._name=='product.product':
            location_headers, inventory_by_location = records.get_stock_by_locations(location_ids)
            for location_id in location_ids:
                columns_headers.append(location_headers.get(location_id))
                
            for data in import_data:
                for location_id in location_ids:
                    data.append(inventory_by_location.get(location_id,{}).get(data[0],0.0))
            
        return request.make_response(self.from_data(columns_headers, import_data),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(model))),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': token})
        
ExportFormat.base = ExportFormatProduct.base



