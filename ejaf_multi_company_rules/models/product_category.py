# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class PosCategory(models.Model):
    _inherit = 'pos.category'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)