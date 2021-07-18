# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def _user_locations(self):
        locations = self.env.user.location_ids
        return [('id', 'in',
                 locations.ids)] if locations else []

    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        )
