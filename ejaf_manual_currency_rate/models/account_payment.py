# -*- coding: utf-8 -*-

import json

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    use_manual_currency_rate = fields.Boolean(string='Use Manual Currency Rate?', readonly=True,
        states={'draft': [('readonly', False)]})
    manual_currency_rate = fields.Float(string='Manual Currency Rate', help='Currency rate to company currency rate.', readonly=True,
        states={'draft': [('readonly', False)]})
    same_company_currency = fields.Boolean(compute='check_same_company_currency', store=1)

    @api.constrains('use_manual_currency_rate', 'manual_currency_rate')
    def check_manual_currency_rate(self):
        for rec in self:
            if rec.use_manual_currency_rate and float_compare(rec.manual_currency_rate, 0.0, 5) <= 0:
                raise ValidationError(_('The manual currency rate must be strictly positive.'))

    @api.depends('company_id', 'company_id.currency_id', 'currency_id')
    def check_same_company_currency(self):
        for rec in self:
            company = rec.company_id
            if rec.currency_id == company.currency_id:
                rec.same_company_currency = True
            else:
                rec.same_company_currency = False

    @api.onchange('use_manual_currency_rate', 'currency_id', 'company_id')
    def onchange_use_manual_currency_rate(self):
        company = self.company_id
        if self.currency_id == company.currency_id:
            self.use_manual_currency_rate = False
            self.manual_currency_rate = 0.0
        if not self.use_manual_currency_rate:
            self.manual_currency_rate = 0.0

    @api.onchange('destination_journal_id')
    def _onchange_destination_journal(self):
        if self.destination_journal_id:
            if self.destination_journal_id.currency_id:
                self.currency_id = self.destination_journal_id.currency_id

    # @api.onchange('journal_id', 'use_manual_currency_rate', 'manual_currency_rate')
    # def _onchange_journal(self):
    #     if self.use_manual_currency_rate and self.manual_currency_rate:
    #         return super(AccountPaymentInherit, self.with_context(manual_currency_id=self.currency_id,
    #                                                            manual_currency_rate=self.manual_currency_rate))._onchange_journal()
    #     return super(AccountPaymentInherit, self)._onchange_journal()

    # @api.onchange('currency_id', 'use_manual_currency_rate', 'manual_currency_rate')
    # def _onchange_currency(self):
    #     if self.use_manual_currency_rate and self.manual_currency_rate:
    #         return super(AccountPaymentInherit, self.with_context(manual_currency_id=self.currency_id,
    #                                                            manual_currency_rate=self.manual_currency_rate))._onchange_currency()
    #     return super(AccountPaymentInherit, self)._onchange_currency()

    @api.onchange('amount', 'currency_id', 'use_manual_currency_rate', 'manual_currency_rate')
    def _onchange_amount(self):
        if self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountPaymentInherit, self.with_context(manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate))._onchange_amount()
        return super(AccountPaymentInherit, self)._onchange_amount()

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'payment_type', 'use_manual_currency_rate', 'manual_currency_rate')
    def _compute_payment_difference(self):
        if len(self) == 1 and self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountPaymentInherit, self.with_context(manual_currency_id=self.currency_id,
                                                                  manual_currency_rate=self.manual_currency_rate))._compute_payment_difference()
        return super(AccountPaymentInherit, self)._compute_payment_difference()

    #########################
    # update currency rates #
    #########################

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        if len(self) == 1 and self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountPaymentInherit, self.with_context(manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate))._compute_payment_amount(invoices, currency, journal, date)
        return super(AccountPaymentInherit, self)._compute_payment_amount(invoices, currency, journal, date)

    def _prepare_payment_moves(self):
        self.ensure_one()
        if self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountPaymentInherit, self.with_context(manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate))._prepare_payment_moves()
        return super(AccountPaymentInherit, self)._prepare_payment_moves()

    def post(self):
        if len(self) == 1 and self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountPaymentInherit, self.with_context(no_exchange_difference=True)).post()
        return super(AccountPaymentInherit, self).post()