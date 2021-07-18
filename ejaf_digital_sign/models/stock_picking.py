# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    user_signature = fields.Binary(string='Signature')
