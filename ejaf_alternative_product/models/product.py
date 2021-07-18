# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools.translate import html_translate


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    product_alternative_ids = fields.One2many(comodel_name="product.alternative", inverse_name="product_tem_id")
