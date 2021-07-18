# -*- coding: utf-8 -*-
import logging
import datetime
from calendar import monthrange
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    contact_partner_id = fields.Many2one(comodel_name="res.partner", string="Customer Contact")

    @api.onchange('date_start')
    def onchange_date_start(self):
        date_today = fields.Date.context_today(self)
        self.recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, self.recurring_interval, date_today, self.recurring_invoice_day)

    @api.model
    def _get_recurring_next_date(self, interval_type, interval, current_date, recurring_invoice_day):
        recurring_next_date = super(SaleSubscription, self)._get_recurring_next_date(interval_type, interval, current_date, recurring_invoice_day)

        # return last day in month of start date

        year = self.date_start.year if self.date_start else current_date.year
        month = self.date_start.month if self.date_start else current_date.month
        if interval_type == 'monthly' and interval == 1 and self.date_start:
            range = monthrange(year, month)
            last_day = range[1]
            recurring_next_date = datetime.date(year, month, last_day)
            self.recurring_invoice_day = recurring_next_date.day
        return recurring_next_date


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    @api.onchange('product_id')
    def onchange_product_quantity(self):
        return super(SaleSubscriptionLine, self).onchange_product_quantity()