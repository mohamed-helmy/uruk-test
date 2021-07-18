# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _default_categ_id(self):

        if self._context.get('created_from_serial'):
            return self.env.company.product_categ_id.id
        else:
            return self._get_default_category_id()

    warranty_period = fields.Integer('Warranty Period')
    warranty_terms = fields.Text('Warranty Terms')
    categ_id = fields.Many2one('product.category', default=_default_categ_id)

