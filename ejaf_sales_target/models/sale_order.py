# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     is_consider_quoted = fields.Boolean(string="Consider Quoted")
#


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_delivered_amount = fields.Float(string="", compute="_compute_qty_delivered_amount", store=True)
    quoted_state = fields.Selection(string="", selection=[('quoted', 'Quoted'), ('unquoted', 'Unquoted')],
                                     default='quoted')

    @api.depends('qty_delivered', 'discount', 'price_unit', 'tax_id')
    def _compute_qty_delivered_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.qty_delivered, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'qty_delivered_amount': taxes['total_excluded'],
            })