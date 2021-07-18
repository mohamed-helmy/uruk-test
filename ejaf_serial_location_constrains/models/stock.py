# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        """
        Disable deliver or transfer any serial no. not in the source location of picking
        """
        for line in self:
            available_qty = sum(self.env['stock.quant'].sudo().search(
                [('lot_id', '=', line.lot_id.id), ('product_id', '=', line.product_id.id),
                 ('location_id', '=', line.picking_id.location_id.id)]).mapped("quantity"))


            if line.product_id.tracking != 'none' and line.lot_id and line.picking_id and \
                            line.company_id and not line.company_id.track_serial_sales_only:


                if (line.picking_id.location_id != line.location_id) or \
                        (line.picking_id.location_id == line.location_id and available_qty < line.qty_done):
                    raise ValidationError("Serial No {} For product {} must be availble in location {} to transfer it ".
                                          format(line.lot_id.name, line.product_id.name,
                                                 line.picking_id.location_id.display_name))
        return super(StockMoveLine, self)._action_done()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, values):
        picking_code = self.env['stock.picking.type'].sudo().browse(values.get("picking_type_id")).code
        if picking_code != 'internal':
            if not values.get('backorder_id', False) and (self.env.context.get('contact_display') or
                self.env.context.get('active_model') in ['sale.order', 'purchase.order']) and not self.env.is_admin():

                raise AccessError(_("Only administrators can create Receipt/Delivery manually"))
        return super(StockPicking, self).create(values)
