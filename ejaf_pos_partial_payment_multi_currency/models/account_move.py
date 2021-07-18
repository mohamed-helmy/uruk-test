# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.point_of_sale.models.account_move import AccountMove as POS_AccountMove


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    pos_order_id = fields.Many2one('pos.order', string='POS Order', copy=False)

    # work around to fix mark invoice as paid in pos order partial payment
    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        return super(POS_AccountMove, self)._compute_amount()

POS_AccountMove._compute_amount = AccountMoveInherit._compute_amount


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    pos_order_id = fields.Many2one('pos.order', string='POS Order', compute='get_related_pos_order', inverse='set_related_pos_order', store=1)
    move_pos_order_id = fields.Many2one('pos.order', string='Move POS Order', copy=False)

    @api.depends('move_id', 'move_id.pos_order_id', 'move_pos_order_id')
    def  get_related_pos_order(self):
        for line in self:
            if line.move_id.is_invoice(include_receipts=True):
                line.pos_order_id = line.move_id.pos_order_id.id if line.move_id.pos_order_id else False
            else:
                line.pos_order_id = line.move_pos_order_id.id if line.move_pos_order_id else False

    @api.depends('move_id', 'pos_order_id')
    def  set_related_pos_order(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                line.move_pos_order_id = line.pos_order_id if line.pos_order_id else False
