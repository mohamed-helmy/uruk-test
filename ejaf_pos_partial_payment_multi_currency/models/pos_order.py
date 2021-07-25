# -*- coding: utf-8 -*-

import logging
import psycopg2

from odoo import fields, api, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    currency_id = fields.Many2one('res.currency', related=False, string="Currency")
    amount_return_currency_id = fields.Many2one('res.currency', string="Amount Return Currency")

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns number pos_order id
        """
        to_invoice = order['to_invoice'] if not draft else False
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        if to_invoice:
            pos_order.with_context(default_pos_order_id=pos_order.id,
                                   force_company=self.env.user.company_id.id).action_pos_order_invoice()
            if pos_order.account_move.state == 'draft':
                pos_order.account_move.sudo().with_context(force_company=self.env.user.company_id.id,
                                                           default_pos_order_id=pos_order.id).post()

        return pos_order.id

    def action_pos_order_paid(self):
        if not float_is_zero(self.amount_total - self.amount_paid, precision_rounding=self.currency_id.rounding):
            self.write({'state': 'paid'})
            return self.create_picking()
        return super(PosOrderInherit, self).action_pos_order_paid()

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrderInherit, self)._order_fields(ui_order)
        res['currency_id'] = ui_order.get('currency').get('id')
        res['amount_return_currency_id'] = ui_order.get('amount_return_currency').get('id')
        return res

    def _prepare_invoice_vals(self):
        vals = super(PosOrderInherit, self)._prepare_invoice_vals()
        vals.update({
            'currency_id': self.currency_id.id if self.currency_id else self.pricelist_id.currency_id.id
        })
        return vals

    def add_payment(self, data):
        res = super(PosOrderInherit, self).add_payment(data)
        amount_paid = 0.0
        for p in self.payment_ids:
            currency = self.currency_id or self.session_id.currency_id
            if p.currency_id == currency:
                amount_paid += p.amount
            else:
                amount_paid += p.currency_id._convert(p.amount, currency, self.company_id,
                                                      p.payment_date or fields.Date.context_today(self), round=True)
        self.amount_paid = amount_paid
        return res

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        """Create account.bank.statement.lines from the dictionary given to the parent function.

        If the payment_line is an updated version of an existing one, the existing payment_line will first be
        removed before making a new one.
        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param order: Order object the payment lines should belong to.
        :type order: pos.order
        :param pos_session: PoS session the order was created in.
        :type pos_session: pos.session
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        """
        prec_acc = order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
        order_bank_statement_lines.unlink()
        for payments in pos_order['statement_ids']:
            if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                order.add_payment(self._payment_fields(order, payments[2]))

        amount_paid = 0.0
        for p in order.payment_ids:
            currency = order.currency_id or order.session_id.currency_id
            if p.currency_id == currency:
                amount_paid += p.amount
            else:
                amount_paid += p.currency_id._convert(p.amount, currency, order.company_id, p.payment_date or fields.Date.context_today(self), round=True)

        order.amount_paid = amount_paid

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            amount_return = pos_order['amount_return']

            currency_id = order.amount_return_currency_id or order.currency_id
            # if order.amount_return_currency_id and order.currency_id and order.amount_return_currency_id != order.currency_id:
            #     amount_return = order.currency_id._convert(
            #         amount_return, order.amount_return_currency_id, order.company_id,
            #         fields.Date.context_today(self),
            #         round=True)

            if currency_id:
                cash_payment_method = pos_session.payment_method_ids.filtered(lambda x: x.is_cash_count and x.currency_id == currency_id)[:1]
                if not cash_payment_method:
                    raise UserError(_("No cash statement found for this session with currency %s. Unable to record returned cash.") % (currency_id.name))
            else:
                cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
                if not cash_payment_method:
                    raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'amount': -amount_return,
                'payment_date': fields.Date.context_today(self),
                'payment_method_id': cash_payment_method.id,
                'other_currency_id': currency_id.id if currency_id else False,
            }
            order.add_payment(return_payment_vals)


    def set_pack_operation_lot(self, picking=None):
        """
        Override to create Serial/Lot number in pack operations to mark the pack operation done.
        """

        StockProductionLot = self.env['stock.production.lot']
        PosPackOperationLot = self.env['pos.pack.operation.lot']
        has_wrong_lots = False

        for order in self:
            for move in (picking or self.picking_id).move_lines:
                picking_type = (picking or self.picking_id).picking_type_id
                lots_necessary = True
                if picking_type:
                    lots_necessary = picking_type and picking_type.use_existing_lots
                qty_done = 0
                pack_lots = []
                pos_pack_lots = PosPackOperationLot.search([('order_id', '=', order.id), ('product_id', '=', move.product_id.id)])

                if pos_pack_lots and lots_necessary:
                    for pos_pack_lot in pos_pack_lots:
                        stock_production_lot = StockProductionLot.search([('name', '=', pos_pack_lot.lot_name), ('product_id', '=', move.product_id.id)])
                        _logger.debug(
                            "///////////////////////////////////////////////// pos_pack_lots {}".format(pos_pack_lots))

                        if not stock_production_lot:
                            stock_production_lot = StockProductionLot.create({'product_id': move.product_id.id,
                                                                              'name': pos_pack_lot.lot_name})
                            # a serialnumber always has a quantity of 1 product, a lot number takes the full quantity of the order line
                            qty = 1.0
                            if stock_production_lot.product_id.tracking == 'lot':
                                qty = abs(pos_pack_lot.pos_order_line_id.qty)
                            qty_done += qty
                            pack_lots.append({'lot_id': stock_production_lot.id, 'qty': qty})

                elif move.product_id.tracking == 'none' or not lots_necessary:
                    qty_done = move.product_uom_qty
                else:
                    has_wrong_lots = True
                for pack_lot in pack_lots:

                    lot_id, qty = pack_lot['lot_id'], pack_lot['qty']
                    self.env['stock.move.line'].create({
                        'picking_id': move.picking_id.id,
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': qty,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id': lot_id,
                    })
                if not pack_lots and not float_is_zero(qty_done, precision_rounding=move.product_uom.rounding):
                    if len(move._get_move_lines()) < 2:
                        move.quantity_done = qty_done
                    else:
                        move._set_quantity_done(qty_done)
        return has_wrong_lots
