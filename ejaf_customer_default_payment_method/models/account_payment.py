# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields
_logger = logging.getLogger(__name__)


class Payment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        result = super(Payment, self)._onchange_partner_id()
        if self.partner_type == 'customer' and self.partner_id and self.partner_id.default_payment_method_id:
            self.journal_id = self.partner_id.default_payment_method_id.id
        return result

