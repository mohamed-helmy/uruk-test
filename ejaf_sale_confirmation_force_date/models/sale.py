# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    force_confirmation_date = fields.Datetime(default=fields.Datetime.now)

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        self.write({'date_order': self.force_confirmation_date})
        return result



