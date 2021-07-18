# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    partner_id = fields.Many2one('res.partner', string='Contact', related='move_id.partner_id')
