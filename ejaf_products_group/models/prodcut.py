# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, AccessError
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights Can create "))
        return super(ProductTemplate, self).create(values)

    def write(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can edit "))
        return super(ProductTemplate, self).write(values)

    def unlink(self):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can delete "))
        return super(ProductTemplate, self).unlink()


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights Can create "))
        return super(Product, self).create(values)

    def write(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can edit "))
        return super(Product, self).write(values)

    def unlink(self):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can delete "))
        return super(Product, self).unlink()


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    @api.model
    def create(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights Can create "))
        return super(ProductAttribute, self).create(values)

    def write(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can edit "))
        return super(ProductAttribute, self).write(values)

    def unlink(self):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can delete "))
        return super(ProductAttribute, self).unlink()


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def create(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights Can create "))
        return super(ProductAttributeValue, self).create(values)

    def write(self, values):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can edit "))
        return super(ProductAttributeValue, self).write(values)

    def unlink(self):
        if not self.env.user.has_group('ejaf_products_group.group_product_full_access') and not self._context.get('force_company', False):
            raise AccessError(_("Only user with group Products Full Access Rights can delete "))
        return super(ProductAttributeValue, self).unlink()

