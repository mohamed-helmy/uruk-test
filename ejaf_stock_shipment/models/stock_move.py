# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    shipment_no = fields.Char(string='Shipment No')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    shipment_no = fields.Char(string='Shipment No', related='move_id.shipment_no')

   