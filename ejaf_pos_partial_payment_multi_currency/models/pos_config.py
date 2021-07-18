# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    allow_partial_payment = fields.Boolean(string="Allow Partial Payment")


class PosPaymentInherit(models.Model):
    _inherit = 'pos.payment.method'

    currency_id = fields.Many2one('res.currency', string='Currency', compute='get_currency', inverse='set_currency')
    temp_currency_id = fields.Many2one('res.currency', string='Currency')

    def get_currency(self):
        for rec in self:
            rec.currency_id = rec.temp_currency_id or rec.cash_journal_id.currency_id or rec.cash_journal_id.company_id.currency_id

    def set_currency(self):
        for rec in self:
            rec.temp_currency_id = rec.currency_id
