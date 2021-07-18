# -*- coding: utf-8 -*-

import json

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

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

    @api.onchange('date', 'currency_id', 'use_manual_currency_rate', 'manual_currency_rate')
    def _onchange_currency(self):
        return super(AccountMoveInherit, self)._onchange_currency()

    def action_invoice_register_payment(self):
        if self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountMoveInherit, self.with_context(default_use_manual_currency_rate=True,
                                                               default_manual_currency_rate=self.manual_currency_rate, manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate)).action_invoice_register_payment()
        return super(AccountMoveInherit, self).action_invoice_register_payment()

    #########################
    # update currency rates #
    #########################

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        if self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountMoveInherit, self.with_context(manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate))._recompute_tax_lines(recompute_tax_base_amount)
        return super(AccountMoveInherit, self)._recompute_tax_lines(recompute_tax_base_amount)

    def _recompute_cash_rounding_lines(self):
        if self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountMoveInherit, self.with_context(manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate))._recompute_cash_rounding_lines()
        return super(AccountMoveInherit, self)._recompute_cash_rounding_lines()

    def _get_reconciled_info_JSON_values(self):
        if self.use_manual_currency_rate and self.manual_currency_rate:
            return super(AccountMoveInherit, self.with_context(manual_currency_id=self.currency_id,
                                                               manual_currency_rate=self.manual_currency_rate))._get_reconciled_info_JSON_values()
        return super(AccountMoveInherit, self)._get_reconciled_info_JSON_values()

    # Overwritten to use manual currency rate
    def _inverse_amount_total(self):
        for move in self:
            if len(move.line_ids) != 2 or move.type != 'entry':
                continue

            to_write = []

            if move.currency_id != move.company_id.currency_id:
                amount_currency = abs(move.amount_total)
                if move.use_manual_currency_rate and move.manual_currency_rate:
                    balance = move.currency_id.with_context(manual_currency_id=move.currency_id,
                                                            manual_currency_rate=move.manual_currency_rate)._convert(
                        amount_currency, move.currency_id, move.company_id, move.date)
                else:
                    balance = move.currency_id._convert(amount_currency, move.currency_id, move.company_id, move.date)
            else:
                balance = abs(move.amount_total)
                amount_currency = 0.0

            for line in move.line_ids:
                if abs(line.balance) != balance:
                    to_write.append((1, line.id, {
                        'debit': line.balance > 0.0 and balance or 0.0,
                        'credit': line.balance < 0.0 and balance or 0.0,
                        'amount_currency': line.balance > 0.0 and amount_currency or -amount_currency,
                    }))

            move.write({'line_ids': to_write})

    # Overwritten to use manual currency rate
    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' or move.invoice_payment_state != 'not_paid' or not move.is_invoice(
                    include_receipts=True):
                continue
            pay_term_line_ids = move.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                      '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'),
                      ('journal_id.post_at', '=', 'bank_rec'),
                      ('partner_id', '=', move.commercial_partner_id.id),
                      ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                      ('amount_residual_currency', '!=', 0.0)]

            if move.is_inbound():
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'move_id': move.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = move.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == move.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency = line.company_id.currency_id
                        if move.use_manual_currency_rate and move.manual_currency_rate:
                            amount_to_show = currency.with_context(manual_currency_id=move.currency_id,
                                                                   manual_currency_rate=move.manual_currency_rate)._convert(
                                abs(line.amount_residual), move.currency_id,
                                move.company_id,
                                line.date or fields.Date.today())
                        else:
                            amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id,
                                                               move.company_id,
                                                               line.date or fields.Date.today())
                    if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
                        continue
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, move.currency_id.decimal_places],
                        'payment_date': fields.Date.to_string(line.date),
                    })
                info['title'] = type_payment
                move.invoice_outstanding_credits_debits_widget = json.dumps(info)
                move.invoice_has_outstanding = True


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    #########################
    # update currency rates #
    #########################

    def _get_computed_price_unit(self):
        if self.move_id.use_manual_currency_rate and self.move_id.manual_currency_rate:
            return super(AccountMoveLineInherit, self.with_context(manual_currency_id=self.move_id.currency_id,
                                                               manual_currency_rate=self.move_id.manual_currency_rate))._get_computed_price_unit()
        return super(AccountMoveLineInherit, self)._get_computed_price_unit()

    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None,
                                      date=None):
        if self.move_id.use_manual_currency_rate and self.move_id.manual_currency_rate:
            return super(AccountMoveLineInherit, self.with_context(manual_currency_id=self.move_id.currency_id, manual_currency_rate=self.move_id.manual_currency_rate))._get_fields_onchange_subtotal(price_subtotal, move_type, currency, company, date)
        return super(AccountMoveLineInherit, self)._get_fields_onchange_subtotal(price_subtotal, move_type, currency, company, date)