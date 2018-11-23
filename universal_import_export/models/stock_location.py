
from odoo import models, api

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    @api.model
    def get_export_stock_locations(self):
        warehouses = self.env['stock.warehouse'].sudo().search([('company_id','=',self.env.user.company_id.id)])
        
        return self.sudo().search_read([('id','not in', warehouses.mapped('lot_stock_id').ids),
                                        ('usage','=','internal'),
                                        ('company_id','=',self.env.user.company_id.id)],
                                       fields=['display_name','id'])
    
    @api.model
    def get_export_stock_warehouse(self):
        return self.env['stock.warehouse'].sudo().search_read([('company_id','=',self.env.user.company_id.id)],fields=['name','id','code'])