# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class TransferRequest(models.Model):
    _inherit = 'internal.transfer.request'

    sale_subscription_id = fields.Many2one('sale.subscription', string="Subscription", ondelete="cascade")
