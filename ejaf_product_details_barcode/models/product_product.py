# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.osv import expression


class Product(models.Model):
    _inherit = 'product.product'

    def get_product_quants(self):
        location_domain = self._get_domain_locations()[0]
        domain = expression.AND([[('product_id', 'in', self.ids)], location_domain])
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all([product.tracking == 'none' for product in self])
        self = self.with_context(hide_location=hide_location, hide_lot=hide_lot)

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_id=self.product_tmpl_id.id)
        ctx = dict(self.env.context)
        ctx.update({'no_at_date': True})
        quants = self.env['stock.quant'].with_context(ctx).search(domain)
        data = []
        for q in quants:
            data.append([q.location_id.display_name, q.inventory_quantity])
        return data

    @api.model
    def get_all_products_by_barcode(self):
        res = super(Product, self).get_all_products_by_barcode()
        ids = []
        for key in res:
            if res[key].get('id', False) and res[key].get('uom_id', False):
                ids.append(res[key]['id'])
        products_to_read = self.env['product.product'].sudo().browse(ids)
        for key in res:
            for p in products_to_read:
                if res[key].get('id', False) and res[key]['id'] == p.id:
                    res[key]['list_price'] = p.list_price
                    res[key]['qty_available'] = p.qty_available
                    res[key]['currency_symbol'] = p.currency_id.symbol if p.currency_id else False
                    res[key]['currency_symbol_after'] = True if p.currency_id and p.currency_id.position == 'after' else False
                    res[key]['currency_symbol_before'] = True if p.currency_id and p.currency_id.position == 'before' else False
                    res[key]['qty_per_location'] = p.get_product_quants()
        return res