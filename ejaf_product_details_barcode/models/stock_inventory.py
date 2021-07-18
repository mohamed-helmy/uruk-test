# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round

import json


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def open_product_details(self):
        action = self.env.ref('ejaf_product_details_barcode.stock_barcode_product_details_client_action').read()[0]
        params = {
            'model': 'product.product',
        }
        action = dict(action, target='fullscreen', params=params)
        return action