# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        res = super(PurchaseOrder, self.with_context(mail_post_autofollow=False)).message_post(**kwargs)
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'draft').write({'state': 'sent'})
        self.message_unsubscribe([self.partner_id.id])
        return res
