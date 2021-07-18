# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    sdr_journal_id = fields.Many2one('account.journal', string='Default Journal', related='company_id.sdr_journal_id', readonly=False)
    sdr_product_id = fields.Many2one('product.product', string='Default Discount Product', related='company_id.sdr_product_id', readonly=False)

