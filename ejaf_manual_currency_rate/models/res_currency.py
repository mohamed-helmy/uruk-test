# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCurrencyInherit(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        res = super(ResCurrencyInherit, self)._get_conversion_rate(from_currency, to_currency, company, date)
        if self._context.get('manual_currency_id', False) and self._context.get('manual_currency_rate', False):
            currency_rates = (from_currency + to_currency)._get_rates(company, date)
            if self._context.get('manual_currency_id') == from_currency:
                return currency_rates.get(to_currency.id) / self._context.get('manual_currency_rate') if self._context.get('manual_currency_rate') else 1
            elif self._context.get('manual_currency_id') == to_currency:
                return self._context.get('manual_currency_rate') / currency_rates.get(from_currency.id)
        return res
