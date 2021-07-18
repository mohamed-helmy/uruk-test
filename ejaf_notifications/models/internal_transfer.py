# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError


class InternalTransferRequest(models.Model):
    _inherit = 'internal.transfer.request'

    def action_submit(self):
        result = super(InternalTransferRequest, self).action_submit()
        self.send_int_transfer_req_notifications()
        return result

    def send_int_transfer_req_notifications(self):
        discussion_subtype = self.env.ref('mail.mt_comment')
        access_group = self.env.ref(
            'ejaf_stock_internal_transfer_request.group_stock_request_manager')
        users = access_group.users
        partner_ids = [u.partner_id.id for u in users]
        self.message_post(
            partner_ids=partner_ids,
            subject=_('Internal Transfer Req Submitted'),
            body=_('Internal Transfer Req %s Submitted') % (self.name),
            subtype_id=discussion_subtype.id,
        )
