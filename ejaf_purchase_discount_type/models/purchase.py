# -*- coding: utf-8 -*-

from odoo import fields, models, api

class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Type', default='percentage')
    discount_amount = fields.Float(string='Disc Amount')
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

    @api.onchange('discount_type', 'discount_amount', 'discount', 'product_qty', 'price_unit', 'taxes_id')
    def onchange_discount_type(self):
        if self.discount_type == 'fixed':
            self.discount = 0.0
            self.discount = (self.discount_amount / (self.product_qty * self.price_unit)) * 100 if (self.product_qty * self.price_unit) else 0.0
        else:
            self.discount_amount = self.product_qty * self.price_unit * (self.discount / 100.0)

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        return super(PurchaseOrderLineInherit, self)._compute_amount()

    def _prepare_compute_all_values(self):
        res = super(PurchaseOrderLineInherit, self)._prepare_compute_all_values()
        price_unit = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        res['price_unit'] = price_unit
        return res

    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLineInherit, self)._prepare_account_move_line(move)
        res.update({
            'discount_type': self.discount_type,
            'discount': self.discount,
            'discount_amount': self.discount_amount,
        })
        return res