# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    sdr_journal_id = fields.Many2one('account.journal')
    sdr_product_id = fields.Many2one('product.product')

