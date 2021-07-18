# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    internal_request_id = fields.Many2one(comodel_name="internal.transfer.request", string='Stock Request')
    is_transit_stage = fields.Boolean(string="Add Transit Stage")
    transit_company = fields.Char(string="Transit company")
    transit_type = fields.Char(string="Transit Type")

    def action_in_transit(self):
        self.transit_type = 'InTransit'
