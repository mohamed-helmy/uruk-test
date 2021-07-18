# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)

        result.send_so_notifications()
        return result

    def send_so_notifications(self):
        discussion_subtype = self.env.ref('mail.mt_comment')
        so_alert_notification_users = self.team_id.team_leader_ids
        users = so_alert_notification_users
        partner_ids = [u.partner_id.id for u in users]
        self.message_post(
            partner_ids=partner_ids,
            subject=_('Sales Order Created'),
            body=_('Sales Order %s Created') % (self.name),
            subtype_id=discussion_subtype.id,
        )
