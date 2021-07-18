# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        result = super(PurchaseOrder, self).create(vals)

        result.send_purchase_order_notifications()
        return result

    def send_purchase_order_notifications(self):
        discussion_subtype = self.env.ref('mail.mt_comment')
        access_group = self.env.ref(
            'purchase.group_purchase_user')
        users = access_group.users.filtered(lambda u:u.company_id == self.company_id)
        partner_ids = [u.partner_id.id for u in users]
        self.message_post(
            partner_ids=partner_ids,
            subject=_('PO Created'),
            body=_('PO %s Created') % (self.name),
            subtype_id=discussion_subtype.id,
        )
