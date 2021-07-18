# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    brand_id = fields.Many2one(related='product_id.brand_id', comodel_name="product.brand", string="Brand", store=True)

