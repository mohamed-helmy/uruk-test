# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    subscription_asset_product_ids = fields.One2many('subscription.asset.product', 'subscription_id',
                                                     string="Assets products", copy=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_asset_product_ids = fields.One2many('sale.asset.product', 'sale_order_id',
                                             string="Assets products")

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for record in self:
            subscriptions = record.order_line.mapped('subscription_id')
            if subscriptions and record.sale_asset_product_ids:
                subscription_asset_products = []
                for line in record.sale_asset_product_ids:
                    subscription_asset_products.append((0, 0, {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'model_id': line.model_id.id,
                    }))
                for subscription in subscriptions:
                    subscription.sudo().write({"subscription_asset_product_ids": subscription_asset_products})

        return res


class SaleAssetProduct(models.TransientModel):
    _name = "sale.asset.product"
    _description = 'Sale Assets products'

    sale_order_id = fields.Many2one('sale.order', required=True, ondelete="cascade")
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


