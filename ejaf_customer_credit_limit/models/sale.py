# -*- coding: utf-8 -*-

from odoo import api, models, _, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        if partner.allow_over_credit:
            return True
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.user_type_id.name', 'in',
              ['Receivable', 'Payable'])]
        )
        confirmed_sale_orders = self.search([('partner_id', '=', partner.id), ('state', '=', 'sale')])
        debit, credit = 0.0, 0.0
        amount_total = 0.0
        amount_total_invoiced = 0.0
        amount_invoiced_unpaid = 0.0
        for o in confirmed_sale_orders:
            if o.currency_id != self.env.company.currency_id:
                amount_total += o.currency_id._convert(o.amount_total, self.env.company.currency_id, self.env.company, o.date_order, round=round)
            else:
                amount_total += o.amount_total

            for inv in o.invoice_ids:
                if inv.currency_id != self.env.company.currency_id:
                    amount_total_invoiced += inv.currency_id._convert(inv.amount_total, self.env.company.currency_id,
                                                           self.env.company, inv.invoice_date or fields.Date.today(), round=True)
                    amount_invoiced_unpaid += inv.currency_id._convert(inv.amount_residual, self.env.company.currency_id,
                                                                      self.env.company,
                                                                      inv.invoice_date or fields.Date.today(),
                                                                      round=True)
                else:
                    amount_total_invoiced += inv.amount_total
                    amount_invoiced_unpaid += inv.amount_residual

        amount_total_to_invoice = amount_total - amount_total_invoiced
        for line in movelines:
            credit += line.credit
            debit += line.debit
        partner_credit_limit = partner.credit_limit
        partner_credit_balance = round((amount_total_to_invoice + debit - credit), 5)
        partner_unpaid_amount = amount_invoiced_unpaid + amount_total_to_invoice
        available_credit_limit = (partner_credit_limit - partner_credit_balance) if float_compare((partner_credit_limit - partner_credit_balance), 0, 5) > 0 else 0.0

        if self.currency_id != self.env.company.currency_id:
            current_amount_total = self.currency_id._convert(self.amount_total, self.env.company.currency_id, self.env.company,
                                                   self.date_order, round=round)
        else:
            current_amount_total = self.amount_total
        partner_balance_after_sale_order = partner_credit_balance + current_amount_total
        if float_compare(partner_balance_after_sale_order, partner_credit_limit, 5) > 0:
                msg = 'Customer credit limit amount = %s %s\n' \
                      'Customer credit balance = %s %s\n' \
                      'Customer unpaid amount = %s %s\n' \
                      'Customer available credit limit amount = %s %s\n' \
                      'Check "%s" accounts or credit limits.' % ( partner_credit_limit, self.env.company.currency_id.symbol, partner_credit_balance, self.env.company.currency_id.symbol, partner_unpaid_amount, self.env.company.currency_id.symbol, available_credit_limit, self.env.company.currency_id.symbol, self.partner_id.name)
                raise UserError(_('Sorry, sale order exceeds the customer credit limit. \n' + msg))
        return True

    def action_confirm(self):
        for order in self:
            order.check_limit()
        res = super(SaleOrderInherit, self).action_confirm()
        return res

    # @api.constrains('amount_total')
    # def check_amount(self):
    #     for order in self:
    #         order.check_limit()
