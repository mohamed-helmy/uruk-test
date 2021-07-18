# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    is_service_contract = fields.Boolean(string="Service contract")
    product_serial_ids = fields.One2many(comodel_name="sale.subscription.serial.line",
                                         inverse_name="subscription_id")


class SubscriptionSerialLine(models.Model):
    _name = 'sale.subscription.serial.line'

    lot_id = fields.Many2one(comodel_name="stock.production.lot", string="Lot/Serial Number",
                             required=True)
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    subscription_id = fields.Many2one(comodel_name="sale.subscription")

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            self.product_id = self.lot_id.product_id.id
