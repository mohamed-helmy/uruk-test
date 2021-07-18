# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    available_qty = fields.Float(string="Available qty", compute='compute_available_qty', readonly=True)

    @api.depends('product_id')
    def compute_available_qty(self):
        for line in self:
            if line.product_id:
                line.available_qty = line.product_id.qty_available
            else:
                line.available_qty = 0
