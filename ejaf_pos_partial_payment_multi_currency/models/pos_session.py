# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'


    @api.depends('order_ids.payment_ids.amount', "order_ids.payment_ids.currency_id",
                 "order_ids.payment_ids.payment_date", 'currency_id')
    def _compute_total_payments_amount(self):
        """
            Override original method to calculate total payments with multi currency
        """
        for session in self:
            total_payments_amount = 0.0
            payments = session.order_ids.mapped('payment_ids')
            for payment in payments:
                if payment.currency_id != session.currency_id:
                    payment_amount = payment.currency_id._convert(
                        payment.amount, session.currency_id, self.company_id,
                        payment.payment_date or fields.Date.context_today(self),
                        round=True)
                    total_payments_amount += payment_amount
                else:
                    total_payments_amount += payment.amount
            session.total_payments_amount = total_payments_amount

    def _credit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
        """ `partial_move_line_vals` is completed by `credit`ing the given amounts.

        NOTE Amounts in PoS are in the currency of journal_id in the session.config_id.
        This means that amount fields in any pos record are actually equivalent to amount_currency
        in account module. Understanding this basic is important in correctly assigning values for
        'amount' and 'amount_currency' in the account.move.line record.

        :param partial_move_line_vals dict:
            initial values in creating account.move.line
        :param amount float:
            amount derived from pos.payment, pos.order, or pos.order.line records
        :param amount_converted float:
            converted value of `amount` from the given `session_currency` to company currency

        :return dict: complete values for creating 'amount.move.line' record
        """
        pos_order_id = self._context.get('pos_order_id', False)
        statement_currency_id = self._context.get('statement_currency_id', False)
        partial_move_line_vals['pos_order_id'] = pos_order_id.id if pos_order_id else False
        if (self.is_in_company_currency and not pos_order_id) or (self.is_in_company_currency and pos_order_id and pos_order_id.currency_id == self.currency_id and not statement_currency_id) or (self.is_in_company_currency and pos_order_id and pos_order_id.currency_id == self.currency_id and statement_currency_id and pos_order_id.currency_id == statement_currency_id):
            return {
                'debit': -amount if amount < 0.0 else 0.0,
                'credit': amount if amount > 0.0 else 0.0,
                **partial_move_line_vals
            }
        else:
            currency_id = self.currency_id
            if pos_order_id:
                if pos_order_id.currency_id != self.currency_id:
                    currency_id = pos_order_id.currency_id
                if statement_currency_id and statement_currency_id != pos_order_id.currency_id:
                    currency_id = statement_currency_id
            return {
                'debit': -amount_converted if amount_converted < 0.0 else 0.0,
                'credit': amount_converted if amount_converted > 0.0 else 0.0,
                'amount_currency': -amount if currency_id != self.company_id.currency_id else 0.0,
                'currency_id': currency_id.id if currency_id != self.company_id.currency_id else False,
                **partial_move_line_vals
            }

    def _debit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
        """ `partial_move_line_vals` is completed by `debit`ing the given amounts.

        See _credit_amounts docs for more details.
        """

        pos_order_id = self._context.get('pos_order_id', False)
        statement_currency_id = self._context.get('statement_currency_id', False)
        partial_move_line_vals['pos_order_id'] = pos_order_id.id if pos_order_id else False
        if (self.is_in_company_currency and not pos_order_id) or (self.is_in_company_currency and pos_order_id and pos_order_id.currency_id == self.currency_id and not statement_currency_id) or (self.is_in_company_currency and pos_order_id and pos_order_id.currency_id == self.currency_id and statement_currency_id and pos_order_id.currency_id == statement_currency_id):
            return {
                'debit': amount if amount > 0.0 else 0.0,
                'credit': -amount if amount < 0.0 else 0.0,
                **partial_move_line_vals
            }
        else:
            currency_id = self.currency_id
            if pos_order_id:
                if pos_order_id.currency_id != self.currency_id:
                    currency_id = pos_order_id.currency_id
                if statement_currency_id and statement_currency_id != pos_order_id.currency_id:
                    currency_id = statement_currency_id
            return {
                'debit': amount_converted if amount_converted > 0.0 else 0.0,
                'credit': -amount_converted if amount_converted < 0.0 else 0.0,
                'amount_currency': amount if currency_id != self.company_id.currency_id else 0,
                'currency_id': currency_id.id if currency_id != self.company_id.currency_id else False,
                **partial_move_line_vals
            }

    def _update_amounts(self, old_amounts, amounts_to_add, date, round=True):
        pos_order_id = self._context.get('pos_order_id', False)
        statement_currency_id = self._context.get('statement_currency_id', False)
        new_amounts = {}
        for k, amount in old_amounts.items():
            if k == 'amount_converted':
                amount_converted = old_amounts['amount_converted']
                amount_to_convert = amounts_to_add['amount']
                if (self.is_in_company_currency and pos_order_id.currency_id == self.currency_id and not statement_currency_id) or (self.is_in_company_currency and pos_order_id.currency_id == self.currency_id and statement_currency_id and pos_order_id.currency_id == statement_currency_id):
                    amount_converted = amount_converted
                else:
                    amount_converted = amount_converted + self.with_context(pos_order_id=pos_order_id, statement_currency_id=statement_currency_id)._amount_converter(amount_to_convert, date, round)
                new_amounts['amount_converted'] = amount_converted
            elif k == 'amount':
                new_amounts[k] = old_amounts[k] + amounts_to_add[k]
        new_amounts['pos_order_id'] = pos_order_id
        return new_amounts

    def _amount_converter(self, amount, date, round):
        # self should be single record as this method is only called in the subfunctions of self._validate_session
        pos_order_id = self._context.get('pos_order_id', False)
        statement_currency_id = self._context.get('statement_currency_id', False)
        if pos_order_id:
            if statement_currency_id and statement_currency_id != pos_order_id.currency_id:
                return statement_currency_id._convert(amount, self.company_id.currency_id, self.company_id, date, round=round)
            else:
                return pos_order_id.currency_id._convert(amount, self.company_id.currency_id, self.company_id, date,
                                                         round=round)
        return self.currency_id._convert(amount, self.company_id.currency_id, self.company_id, date, round=round)

    def _get_sale_vals(self, key, amount, amount_converted):
        account_id, sign, tax_keys, currency_id = key
        key = (account_id, sign, tax_keys)

        account_id, sign, tax_keys = key
        tax_ids = set(tax[0] for tax in tax_keys)
        applied_taxes = self.env['account.tax'].browse(tax_ids)
        title = 'Sales' if sign == 1 else 'Refund'
        name = '%s untaxed' % title
        if applied_taxes:
            name = '%s with %s' % (title, ', '.join([tax.name for tax in applied_taxes]))
        base_tags = applied_taxes\
            .mapped('invoice_repartition_line_ids' if sign == 1 else 'refund_repartition_line_ids')\
            .filtered(lambda line: line.repartition_type == 'base')\
            .tag_ids
        partial_vals = {
            'name': name,
            'account_id': account_id,
            'move_id': self.move_id.id,
            'tax_ids': [(6, 0, tax_ids)],
            'tag_ids': [(6, 0, base_tags.ids)],
        }
        return self._credit_amounts(partial_vals, amount, amount_converted)

    # def _create_account_move(self):
    #     return super(PosSessionInherit, self.with_context(check_move_validity=False))._create_account_move()

    # def _create_account_move(self):
    #     """ Create account.move and account.move.line records for this session.
    #
    #     Side-effects include:
    #         - setting self.move_id to the created account.move record
    #         - creating and validating account.bank.statement for cash payments
    #         - reconciling cash receivable lines, invoice receivable lines and stock output lines
    #     """
    #     journal = self.config_id.journal_id
    #     # Passing default_journal_id for the calculation of default currency of account move
    #     # See _get_default_currency in the account/account_move.py.
    #     account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
    #         'journal_id': journal.id,
    #         'date': fields.Date.context_today(self),
    #         'ref': self.name,
    #     })
    #     self.write({'move_id': account_move.id})
    #
    #     data = {}
    #     data = self._accumulate_amounts(data)
    #     data = self._create_non_reconciliable_move_lines(data)
    #     data = self._create_cash_statement_lines_and_cash_move_lines(data)
    #     data = self._create_invoice_receivable_lines(data)
    #     data = self._create_stock_output_lines(data)
    #     data = self._create_extra_move_lines(data)
    #     data = self._reconcile_account_move_lines(data)

    def _accumulate_amounts(self, data):
        # Accumulate the amounts for each accounting lines group
        # Each dict maps `key` -> `amounts`, where `key` is the group key.
        # E.g. `combine_receivables` is derived from pos.payment records
        # in the self.order_ids with group key of the `payment_method_id`
        # field of the pos.payment record.
        amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
        tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'pos_order_id': False}
        split_receivables = defaultdict(amounts)
        split_receivables_cash = defaultdict(amounts)
        combine_receivables = defaultdict(amounts)
        combine_receivables_cash = defaultdict(amounts)
        invoice_receivables = defaultdict(amounts)
        sales = defaultdict(amounts)
        taxes = defaultdict(tax_amounts)
        stock_expense = defaultdict(amounts)
        stock_output = defaultdict(amounts)
        # Track the receivable lines of the invoiced orders' account moves for reconciliation
        # These receivable lines are reconciled to the corresponding invoice receivable lines
        # of this session's move_id.
        order_account_move_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
        rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
        for order in self.order_ids:
            # Combine pos receivable lines
            # Separate cash payments for cash reconciliation later.
            for payment in order.payment_ids:
                # amount, date = payment.amount, payment.payment_date
                payment_currency = payment.currency_id
                date = payment.payment_date
                if payment_currency != self.currency_id:
                    amount = payment.amount
                    amount_converted = payment_currency._convert(
                        payment.amount, self.currency_id, self.company_id, date or fields.Date.context_today(self),
                        round=True)
                else:
                    amount = payment.amount
                    amount_converted = 0.0

                if payment.payment_method_id.split_transactions:
                    if payment.payment_method_id.is_cash_count:
                        split_receivables_cash[payment] = self.with_context(pos_order_id=order, statement_currency_id=payment.currency_id)._update_amounts(split_receivables_cash[payment], {'amount': amount, 'amount_converted': amount_converted}, date)
                    else:
                        split_receivables[payment] = self.with_context(pos_order_id=order)._update_amounts(split_receivables[payment], {'amount': amount, 'amount_converted': amount_converted}, date)
                else:
                    key = payment.payment_method_id
                    if payment.payment_method_id.is_cash_count:
                        combine_receivables_cash[key] = self.with_context(pos_order_id=order, statement_currency_id=payment.currency_id)._update_amounts(combine_receivables_cash[key], {'amount': amount, 'amount_converted': amount_converted}, date)
                    else:
                        combine_receivables[key] = self.with_context(pos_order_id=order)._update_amounts(combine_receivables[key], {'amount': amount, 'amount_converted': amount_converted}, date)

            if order.is_invoiced:
                # Combine invoice receivable lines
                # key = order.partner_id.property_account_receivable_id.id
                key = order
                if order.currency_id != self.currency_id:
                    amount = order.amount_paid
                    amount_converted = order.currency_id._convert(
                        order.amount_paid, self.currency_id, self.company_id,
                        order.date_order or fields.Date.context_today(self), round=True)
                else:
                    amount = order.amount_paid
                    amount_converted = 0

                if float_compare(amount, 0.0, 5) > 0:
                    invoice_receivables[key] = self.with_context(pos_order_id=order)._update_amounts(invoice_receivables[key], {'amount': amount, 'amount_converted': amount_converted}, order.date_order)
                # side loop to gather receivable lines by account for reconciliation
                for move_line in order.account_move.line_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable'):
                    order_account_move_receivable_lines[move_line.account_id.id] |= move_line
            else:
                order_taxes = defaultdict(tax_amounts)
                for order_line in order.lines:
                    line = self._prepare_line(order_line)
                    # Combine sales/refund lines
                    sale_key = (
                        # account
                        line['income_account_id'],
                        # sign
                        -1 if line['amount'] < 0 else 1,
                        # for taxes
                        tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),

                        # for currency
                        order.currency_id.id,
                    )

                    if order.currency_id != self.currency_id:
                        amount = line['amount_currency']
                        amount_converted = line['amount']
                    else:
                        amount = line['amount']
                        amount_converted = 0

                    sales[sale_key] = self.with_context(pos_order_id=order)._update_amounts(sales[sale_key], {'amount': amount, 'amount_converted': amount_converted}, line['date_order'])

                    # Combine tax lines
                    for tax in line['taxes']:
                        tax_key = (tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))

                        if order.currency_id != self.currency_id:
                            amount = tax['amount']
                            amount_converted = order.currency_id._convert(
                                tax['amount'], self.currency_id, self.company_id,
                                order.date_order or fields.Date.context_today(self), round=True)
                        else:
                            amount = tax['amount']
                            amount_converted = 0

                        order_taxes[tax_key] = self.with_context(pos_order_id=order)._update_amounts(
                            order_taxes[tax_key],
                            {'amount': amount, 'amount_converted': amount_converted, 'base_amount': tax['base']},
                            tax['date_order'],
                            round=not rounded_globally
                        )
                for tax_key, amounts in order_taxes.items():
                    if rounded_globally:
                        amounts = self._round_amounts(amounts)
                    for amount_key, amount in amounts.items():
                        if amount_key == 'pos_order_id':
                            taxes[tax_key][amount_key] = amount
                        else:
                            taxes[tax_key][amount_key] += amount

                if self.company_id.anglo_saxon_accounting:
                    # Combine stock lines
                    stock_moves = self.env['stock.move'].search([
                        ('picking_id', '=', order.picking_id.id),
                        ('company_id.anglo_saxon_accounting', '=', True),
                        ('product_id.categ_id.property_valuation', '=', 'real_time')
                    ])
                    for move in stock_moves:
                        exp_key = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id
                        out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                        amount = -sum(move.stock_valuation_layer_ids.mapped('value'))

                        if order.currency_id != self.currency_id:
                            amount = order.currency_id._convert(
                                amount, self.currency_id, self.company_id,
                                order.date_order or fields.Date.context_today(self), round=True)
                            amount_converted = amount
                        else:
                            amount = amount
                            amount_converted = 0

                        stock_expense[exp_key] = self.with_context(pos_order_id=order)._update_amounts(stock_expense[exp_key], {'amount': amount, 'amount_converted': amount_converted}, move.picking_id.date)
                        stock_output[out_key] = self.with_context(pos_order_id=order)._update_amounts(stock_output[out_key], {'amount': amount, 'amount_converted': amount_converted}, move.picking_id.date)

                # Increasing current partner's customer_rank
                order.partner_id._increase_rank('customer_rank')

        MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

        data.update({
            'taxes':                               taxes,
            'sales':                               sales,
            'stock_expense':                       stock_expense,
            'split_receivables':                   split_receivables,
            'combine_receivables':                 combine_receivables,
            'split_receivables_cash':              split_receivables_cash,
            'combine_receivables_cash':            combine_receivables_cash,
            'invoice_receivables':                 invoice_receivables,
            'stock_output':                        stock_output,
            'order_account_move_receivable_lines': order_account_move_receivable_lines,
            'MoveLine':                            MoveLine
        })
        return data

    def _create_non_reconciliable_move_lines(self, data):
        # Create account.move.line records for
        #   - sales
        #   - taxes
        #   - stock expense
        #   - non-cash split receivables (not for automatic reconciliation)
        #   - non-cash combine receivables (not for automatic reconciliation)
        taxes = data.get('taxes')
        sales = data.get('sales')
        stock_expense = data.get('stock_expense')
        split_receivables = data.get('split_receivables')
        combine_receivables = data.get('combine_receivables')
        MoveLine = data.get('MoveLine')

        tax_vals = [self.with_context(pos_order_id=amounts['pos_order_id'])._get_tax_vals(key, amounts['amount'], amounts['amount_converted'], amounts['base_amount']) for key, amounts in taxes.items() if amounts['amount']]
        # Check if all taxes lines have account_id assigned. If not, there are repartition lines of the tax that have no account_id.
        tax_names_no_account = [line['name'] for line in tax_vals if line['account_id'] == False]
        if len(tax_names_no_account) > 0:
            error_message = _(
                'Unable to close and validate the session.\n'
                'Please set corresponding tax account in each repartition line of the following taxes: \n%s'
            ) % ', '.join(tax_names_no_account)
            raise UserError(error_message)

        MoveLine.create(
            tax_vals
            + [self.with_context(pos_order_id=amounts['pos_order_id'])._get_sale_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in sales.items()]
            + [self.with_context(pos_order_id=amounts['pos_order_id'])._get_stock_expense_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in stock_expense.items()]
            + [self.with_context(pos_order_id=amounts['pos_order_id'])._get_split_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in split_receivables.items()]
            + [self.with_context(pos_order_id=amounts['pos_order_id'])._get_combine_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in combine_receivables.items()]
        )
        return data

    def _create_cash_statement_lines_and_cash_move_lines(self, data):
        # Create the split and combine cash statement lines and account move lines.
        # Keep the reference by statement for reconciliation.
        # `split_cash_statement_lines` maps `statement` -> split cash statement lines
        # `combine_cash_statement_lines` maps `statement` -> combine cash statement lines
        # `split_cash_receivable_lines` maps `statement` -> split cash receivable lines
        # `combine_cash_receivable_lines` maps `statement` -> combine cash receivable lines
        MoveLine = data.get('MoveLine')
        split_receivables_cash = data.get('split_receivables_cash')
        combine_receivables_cash = data.get('combine_receivables_cash')

        statements_by_journal_id = {statement.journal_id.id: statement for statement in self.statement_ids}
        # handle split cash payments
        split_cash_statement_line_vals = defaultdict(list)
        split_cash_receivable_vals = defaultdict(list)
        for payment, amounts in split_receivables_cash.items():
            statement = statements_by_journal_id[payment.payment_method_id.cash_journal_id.id]
            split_cash_statement_line_vals[statement].append(self._get_statement_line_vals(statement, payment.payment_method_id.receivable_account_id, amounts['amount']))
            split_cash_receivable_vals[statement].append(self.with_context(pos_order_id=amounts['pos_order_id'], statement_currency_id=statement.currency_id)._get_split_receivable_vals(payment, amounts['amount'], amounts['amount_converted']))
        # handle combine cash payments
        combine_cash_statement_line_vals = defaultdict(list)
        combine_cash_receivable_vals = defaultdict(list)
        for payment_method, amounts in combine_receivables_cash.items():
            if not float_is_zero(amounts['amount'] , precision_rounding=self.currency_id.rounding):
                statement = statements_by_journal_id[payment_method.cash_journal_id.id]
                combine_cash_statement_line_vals[statement].append(self._get_statement_line_vals(statement, payment_method.receivable_account_id, amounts['amount']))
                combine_cash_receivable_vals[statement].append(self.with_context(pos_order_id=amounts['pos_order_id'], statement_currency_id=statement.currency_id)._get_combine_receivable_vals(payment_method, amounts['amount'], amounts['amount_converted']))
        # create the statement lines and account move lines
        BankStatementLine = self.env['account.bank.statement.line']
        split_cash_statement_lines = {}
        combine_cash_statement_lines = {}
        split_cash_receivable_lines = {}
        combine_cash_receivable_lines = {}
        for statement in self.statement_ids:
            split_cash_statement_lines[statement] = BankStatementLine.create(split_cash_statement_line_vals[statement])
            combine_cash_statement_lines[statement] = BankStatementLine.create(combine_cash_statement_line_vals[statement])
            split_cash_receivable_lines[statement] = MoveLine.create(split_cash_receivable_vals[statement])
            combine_cash_receivable_lines[statement] = MoveLine.create(combine_cash_receivable_vals[statement])

        data.update(
            {'split_cash_statement_lines':    split_cash_statement_lines,
             'combine_cash_statement_lines':  combine_cash_statement_lines,
             'split_cash_receivable_lines':   split_cash_receivable_lines,
             'combine_cash_receivable_lines': combine_cash_receivable_lines
             })
        return data

    def _create_invoice_receivable_lines(self, data):
        # Create invoice receivable lines for this session's move_id.
        # Keep reference of the invoice receivable lines because
        # they are reconciled with the lines in order_account_move_receivable_lines
        MoveLine = data.get('MoveLine')
        invoice_receivables = data.get('invoice_receivables')

        invoice_receivable_vals = defaultdict(list)
        invoice_receivable_lines = {}
        for order, amounts in invoice_receivables.items():
            receivable_account_id = order.partner_id.property_account_receivable_id.id
            invoice_receivable_vals[receivable_account_id].append(self.with_context(pos_order_id=amounts['pos_order_id'])._get_invoice_receivable_vals(receivable_account_id, amounts['amount'], amounts['amount_converted']))
        for receivable_account_id, vals in invoice_receivable_vals.items():
            invoice_receivable_lines[receivable_account_id] = MoveLine.create(vals)

        data.update({'invoice_receivable_lines': invoice_receivable_lines})
        return data

    def _create_stock_output_lines(self, data):
        # Keep reference to the stock output lines because
        # they are reconciled with output lines in the stock.move's account.move.line
        MoveLine = data.get('MoveLine')
        stock_output = data.get('stock_output')

        stock_output_vals = defaultdict(list)
        stock_output_lines = {}
        for output_account, amounts in stock_output.items():
            stock_output_vals[output_account].append(self.with_context(pos_order_id=amounts['pos_order_id'])._get_stock_output_vals(output_account, amounts['amount'], amounts['amount_converted']))
        for output_account, vals in stock_output_vals.items():
            stock_output_lines[output_account] = MoveLine.create(vals)

        data.update({'stock_output_lines': stock_output_lines})
        return data

    def _get_extra_move_lines_vals(self):
        return []

    def _create_extra_move_lines(self, data):
        # Keep reference to the stock output lines because
        # they are reconciled with output lines in the stock.move's account.move.line
        MoveLine = data.get('MoveLine')

        MoveLine.create(self._get_extra_move_lines_vals())
        return data

    def _reconcile_account_move_lines(self, data):
        # reconcile cash receivable lines
        split_cash_statement_lines = data.get('split_cash_statement_lines')
        combine_cash_statement_lines = data.get('combine_cash_statement_lines')
        split_cash_receivable_lines = data.get('split_cash_receivable_lines')
        combine_cash_receivable_lines = data.get('combine_cash_receivable_lines')
        order_account_move_receivable_lines = data.get('order_account_move_receivable_lines')
        invoice_receivable_lines = data.get('invoice_receivable_lines')
        stock_output_lines = data.get('stock_output_lines')

        for statement in self.statement_ids:
            if not self.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})
            statement.button_confirm_bank()
            all_lines = (
                  split_cash_statement_lines[statement].mapped('journal_entry_ids').filtered(lambda aml: aml.account_id.internal_type == 'receivable')
                | combine_cash_statement_lines[statement].mapped('journal_entry_ids').filtered(lambda aml: aml.account_id.internal_type == 'receivable')
                | split_cash_receivable_lines[statement]
                | combine_cash_receivable_lines[statement]
            )
            accounts = all_lines.mapped('account_id')
            lines_by_account = [all_lines.filtered(lambda l: l.account_id == account) for account in accounts]
            for lines in lines_by_account:
                lines.reconcile()

        # reconcile invoice receivable lines
        for account_id in order_account_move_receivable_lines:
            ##########################################################
            # added part to check aml existence before reconciliation #
            ###########################################################
            if account_id in invoice_receivable_lines:
                for order_mvl in order_account_move_receivable_lines[account_id]:
                    for invoice_mvl in invoice_receivable_lines[account_id]:
                        if invoice_mvl.pos_order_id == order_mvl.pos_order_id:
                            try:
                                (order_mvl | invoice_mvl).reconcile()
                            except:
                                continue

        # reconcile stock output lines
        stock_moves = self.env['stock.move'].search([('picking_id', 'in', self.order_ids.filtered(lambda order: not order.is_invoiced).mapped('picking_id').ids)])
        stock_account_move_lines = self.env['account.move'].search([('stock_move_id', 'in', stock_moves.ids)]).mapped('line_ids')
        for account_id in stock_output_lines:
            try:
                ( stock_output_lines[account_id]
                | stock_account_move_lines.filtered(lambda aml: aml.account_id == account_id)
                ).reconcile()
            except:
                continue
        return data

    def _prepare_line(self, order_line):
        vals = super(PosSessionInherit, self)._prepare_line(order_line)
        if order_line.order_id.currency_id != self.currency_id:
            amount = order_line.order_id.currency_id._convert(
                order_line.price_subtotal, self.currency_id, self.company_id, order_line.order_id.date_order or fields.Date.context_today(self), round=True)
        else:
            amount = order_line.price_subtotal
        vals['currency_id'] = order_line.order_id.currency_id.id
        vals['amount_currency'] = order_line.price_subtotal
        vals['amount'] = amount
        return vals
