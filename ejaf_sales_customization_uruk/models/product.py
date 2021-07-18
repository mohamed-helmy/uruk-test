# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _


class Product(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one('res.company', 'Company', index=1,
                                 default=lambda self: self.env.company)
