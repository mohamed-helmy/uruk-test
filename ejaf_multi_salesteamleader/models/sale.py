# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_user_id')
    def onchange_user_id(self):
        if self.invoice_user_id and self.invoice_user_id.team_member_ids:
            self.team_id = self.invoice_user_id.team_member_ids[0]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id and self.user_id.team_member_ids:
            self.team_id = self.user_id.team_member_ids[0].id


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id and self.user_id.team_member_ids:
            self.team_id = self.user_id.team_member_ids[0].id