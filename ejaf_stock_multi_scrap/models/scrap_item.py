# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class ScrapItem(models.Model):
    _name = "stock.multi.scrap.item" 
    _description = "Multi Scrap item"
    _order = 'id desc'


    def _get_default_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None
   
    multi_scrap_id = fields.Many2one(comodel_name="stock.multi.scrap", ondelete="cascade")

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)

    scrap_qty = fields.Float('Quantity', default=1.0, required=True)
    location_id = fields.Many2one(
         'stock.location', 'Source Location', domain="[('usage', '=', 'internal'), ('company_id', 'in', [company_id, False])]",
         required=True,  default=_get_default_location_id, check_company=True)
    product_id = fields.Many2one(
        'product.product', 'Product', domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=True , check_company=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    owner_id = fields.Many2one('res.partner', 'Owner',  check_company=True)

    package_id = fields.Many2one(
    'stock.quant.package', 'Package',
     check_company=True)
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)
    product_tracking = fields.Selection(string='Tracking', related='product_id.tracking', readonly=True, store=True)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

