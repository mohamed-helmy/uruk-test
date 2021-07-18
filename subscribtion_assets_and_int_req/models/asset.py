# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class Asset(models.Model):
    _inherit = 'account.asset'

    sale_subscription_id = fields.Many2one('sale.subscription', string="Subscription", ondelete="cascade")
