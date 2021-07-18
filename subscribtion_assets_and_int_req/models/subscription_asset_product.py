# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)


class SubscriptionAssetProduct(models.TransientModel):
    _name = "subscription.asset.product"
    _description = 'Subscription Assets products'

    subscription_id = fields.Many2one('sale.subscription', string="Subscription",
                                      required=True, ondelete="cascade")

    name = fields.Char(string="Description", required=True)
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'product')])
    model_id = fields.Many2one('account.asset', required=True,
                               domain=[('state', '=', 'model'), ('asset_type', '=', 'purchase')])

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            return
        else:
            self.name = self.product_id.get_product_multiline_description_sale()
