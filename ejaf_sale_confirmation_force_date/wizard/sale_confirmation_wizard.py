# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SaleWizard(models.TransientModel):
    _name = 'sale.confirmation.wizard'

    force_confirmation_date = fields.Datetime(default=fields.Datetime.now, string="Confirmation Date", required=True)
    order_id = fields.Many2one(comodel_name="sale.order", string="Order", required=True, default=lambda self: self.env.context.get('active_id', False))

    def button_confirm(self):
        order_id = self.order_id or self.env.context.get('active_id', False)
        if order_id:
            order_id.write({"force_confirmation_date": self.force_confirmation_date})
            order_id.action_confirm()
        return True


