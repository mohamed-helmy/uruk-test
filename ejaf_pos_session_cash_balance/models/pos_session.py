# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosSession(models.Model):

    _inherit = "pos.session"

    session_cash_register_ids = fields.Many2many('account.bank.statement', compute='_compute_session_registers', string='Cash Registers')

    def _check_pos_session_balance(self):
        for session in self:
            for statement in session.statement_ids:
                if (statement not in session.session_cash_register_ids) and (statement.balance_end != statement.balance_end_real):
                    statement.write({'balance_end_real': statement.balance_end})

    @api.depends('config_id', 'statement_ids', 'payment_method_ids')
    def _compute_session_registers(self):
        for session in self:
            session.session_cash_register_ids = False
            cash_payment_methods = session.payment_method_ids.filtered('is_cash_count')
            if not cash_payment_methods:
                continue

            cash_registers = []
            for statement in session.statement_ids:
                if cash_payment_methods.filtered(lambda x: x.cash_journal_id == statement.journal_id):
                    cash_registers.append(statement.id)
            session.session_cash_register_ids = [(6, 0, cash_registers)]

    def open_cashbox_pos(self):
        self.ensure_one()
        self.write({'state': 'opening_control'})
        # action = self.cash_register_id.open_cashbox_id()
        # action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
        # action['context']['pos_session_id'] = self.id
        # action['context']['default_pos_id'] = self.config_id.id
        # action['context']['default_payment_method_currency_id'] = self.config_id.currency_id.id
        # return action