# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        self.message_unsubscribe([self.partner_id.id])
