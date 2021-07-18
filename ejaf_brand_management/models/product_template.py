# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

