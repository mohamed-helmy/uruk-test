# -*- coding: utf-8 -*-


import logging

from odoo import api, fields, models, SUPERUSER_ID, _
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_show_details_visible(self):
        """ Hide button `action_show_details` for serial products in receipts
         if Track Serial in Sales Only is Enabled for company.
        """
        res = super(StockMove, self)._compute_show_details_visible()
        for move in self:
            if move.company_id.track_serial_sales_only and move.picking_code == 'incoming':
                move.show_details_visible = False
        return res

    def _compute_display_assign_serial(self):
        res = super(StockMove, self)._compute_display_assign_serial()
        for move in self:
            if move.company_id.track_serial_sales_only and move.picking_code == 'incoming':
                move.display_assign_serial = False
        return res

    def _quantity_done_set(self):
        """
        override to allow receive partial qty for serials if not in sales
        """
        quantity_done = self[0].quantity_done
        for move in self:
            move_lines = move._get_move_lines()
            if not move_lines:
                if quantity_done:
                    # do not impact reservation here
                    move_line = self.env['stock.move.line'].create(
                        dict(move._prepare_move_line_vals(), qty_done=quantity_done))
                    move.write({'move_line_ids': [(4, move_line.id)]})
            #override to allow receive partial qty for serials if not in sales
            elif len(move_lines) == 1 or (move.company_id and move.company_id.track_serial_sales_only and not move.sale_line_id):
                move_lines[0].qty_done = quantity_done
            else:
                raise UserError(_("Cannot set the done quantity from this stock move, work directly with the move lines."))
