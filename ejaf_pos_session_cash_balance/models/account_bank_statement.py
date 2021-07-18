# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    cash_register_total_entry_encoding = fields.Monetary(
        compute='_compute_cash_balance',
        string='Total Cash Transaction',
        readonly=True,
        help="Total of all paid sales orders")
    cash_register_balance_end = fields.Monetary(
        compute='_compute_cash_balance',
        string="Theoretical Closing Balance",
        help="Sum of opening balance and transactions.",
        readonly=True)
    cash_register_difference = fields.Monetary(
        compute='_compute_cash_balance',
        string='Difference',
        help="Difference between the theoretical closing balance and the real closing balance.",
        readonly=True)

    def _compute_cash_balance(self):
        for rec in self:
            session = rec.pos_session_id
            cash_payment_methods = session.payment_method_ids.filtered(lambda x: x.is_cash_count and x.cash_journal_id == rec.journal_id) if session else False
            if cash_payment_methods:
                total_cash_payment = 0.0
                for cash_payment_method in cash_payment_methods:
                    total_cash_payment += sum(session.order_ids.mapped('payment_ids').filtered(
                        lambda payment: payment.payment_method_id == cash_payment_method).mapped('amount'))
                rec.cash_register_total_entry_encoding = rec.total_entry_encoding + (
                    0.0 if session.state == 'closed' else total_cash_payment
                )
                rec.cash_register_balance_end = rec.balance_start + rec.cash_register_total_entry_encoding
                rec.cash_register_difference = rec.balance_end_real - rec.cash_register_balance_end
            else:
                rec.cash_register_total_entry_encoding = 0.0
                rec.cash_register_balance_end = 0.0
                rec.cash_register_difference = 0.0

    def open_new_cashbox_id(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        if context.get('balance'):
            context['statement_id'] = self.id
        action = {
            'name': _('Cash Control'),
            'view_mode': 'form',
            'res_model': 'account.bank.statement.cashbox',
            'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox_footer').id,
            'type': 'ir.actions.act_window',
            'res_id': False,
            'context': context,
            'target': 'new'
        }
        return action

    def open_statement_cashbox(self):
        self.ensure_one()
        action = self.open_new_cashbox_id()
        action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
        action['context']['pos_session_id'] = self._context.get('session_id', False)
        action['context']['default_pos_id'] = self._context.get('pos_id', False)
        return action


class AccountBankStmtCashWizard(models.Model):
    _inherit = 'account.bank.statement.cashbox'

    payment_method_currency_id = fields.Many2one('res.currency', string='Default currency', help='Used to set the default balance in session opening and closing')

    @api.depends('pos_config_ids', 'payment_method_currency_id')
    @api.depends_context('current_currency_id')
    def _compute_currency(self):
        super(AccountBankStmtCashWizard, self)._compute_currency()
        for cashbox in self:
            if cashbox.payment_method_currency_id:
                cashbox.currency_id = cashbox.payment_method_currency_id.id

    @api.model
    def default_get(self, fields):
        vals = super(AccountBankStmtCashWizard, self).default_get(fields)
        config_id = self.env.context.get('default_pos_id')
        payment_method_currency_id = self.env.context.get('default_payment_method_currency_id')
        vals['payment_method_currency_id'] = payment_method_currency_id
        if config_id and payment_method_currency_id:
            config = self.env['pos.config'].browse(config_id)
            cash_boxes = config.default_bank_stmt_cashbox_ids.filtered(lambda x: x.payment_method_currency_id.id == payment_method_currency_id)
            lines = cash_boxes[0].cashbox_lines_ids if cash_boxes else []
            if self.env.context.get('balance', False) == 'start':
                vals['cashbox_lines_ids'] = [
                    [0, 0, {'coin_value': line.coin_value, 'number': line.number, 'subtotal': line.subtotal}] for line
                    in lines]
            else:
                vals['cashbox_lines_ids'] = [[0, 0, {'coin_value': line.coin_value, 'number': 0, 'subtotal': 0.0}] for
                                             line in lines]
        else:
            vals['cashbox_lines_ids'] = False
        return vals

    def set_default_cashbox_by_currency(self):
        self.ensure_one()
        current_session = self.env['pos.session'].browse(self.env.context['pos_session_id'])
        cash_boxes = current_session.config_id.default_bank_stmt_cashbox_ids.filtered(
            lambda x: x.payment_method_currency_id.id == self.payment_method_currency_id.id)
        lines = cash_boxes[0].cashbox_lines_ids if cash_boxes else []
        context = dict(self._context)
        self.cashbox_lines_ids.unlink()
        self.cashbox_lines_ids = [[0, 0, {'coin_value': line.coin_value, 'number': line.number, 'subtotal': line.subtotal}] for line in lines]

        return {
            'name': _('Cash Control'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.cashbox',
            'view_id': self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            'res_id': self.id,
        }