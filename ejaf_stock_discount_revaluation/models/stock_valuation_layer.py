# -*- coding: utf-8 -*-
from odoo import fields, models


class StockValuationLayerInerit(models.Model):
    """Stock Valuation Layer"""

    _inherit = 'stock.valuation.layer'

    is_stock_discount = fields.Boolean(related='stock_landed_cost_id.is_stock_discount')

