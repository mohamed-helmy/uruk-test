# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        res = super(ProductProduct, self.sudo())._name_search(name=name, args=args, operator=operator, limit=limit,
                                                          name_get_uid=SUPERUSER_ID)
        product_ids = self._search([('barcode', 'ilike', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        products = models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))
        for p in products:
            if p in res:
                products.remove(p)
        return res + products
