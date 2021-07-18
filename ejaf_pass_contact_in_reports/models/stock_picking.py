# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            res = super(StockPicking, self).button_validate()
            for move in picking.move_lines:
                move.partner_id = picking.partner_id.id if picking.partner_id else False
            return res
