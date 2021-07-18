# -*- coding: utf-8 -*-

import logging
from odoo import fields, api, models, _
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        result = super(StockMove, self)._action_done(cancel_backorder)
        moves = self.filtered(lambda m: m.state == 'done' and m.sale_line_id)
        if moves:
            for move in moves:
                move_serials = move.move_line_ids.mapped('lot_id')
                if move_serials:
                    move_serials.sudo().filtered(lambda s: not s.partner_id).write({'partner_id': move.partner_id.id})
        return result

