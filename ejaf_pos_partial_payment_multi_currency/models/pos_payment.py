# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosPaymentInherit(models.Model):

    _inherit = "pos.payment"

    currency_id = fields.Many2one('res.currency', string='Currency', related=False, compute='get_currency', inverse='set_currency')
    other_currency_id = fields.Many2one('res.currency', string='Currency')

    def get_currency(self):
        for rec in self:
            rec.currency_id = rec.other_currency_id or rec.payment_method_id.currency_id or rec.pos_order_id.currency_id

    def set_currency(self):
        for rec in self:
            rec.other_currency_id = rec.currency_id

