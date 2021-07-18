# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class TransferRequestReason(models.TransientModel):
    _name = 'transfer.request.reason'

    reject_reason = fields.Text(string="Reject Reason", required=True)

    def reject_request(self):
        int_request = self.env['internal.transfer.request'].browse(self.env.context.get('active_id'))
        if int_request:
            reject_request_vals = {
                'reject_reason': self.reject_reason,
                'state': 'rejected',

            }
            transfer = int_request.sudo().write(reject_request_vals)
        return True
