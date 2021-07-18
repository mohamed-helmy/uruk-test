# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    brand_id = fields.Many2one("product.brand", related='product_tmpl_id.brand_id', string="Brand", store=True)
