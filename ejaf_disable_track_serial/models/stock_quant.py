# -*- coding: utf-8 -*-


import logging

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.quant"

    @api.constrains('quantity')
    def check_quantity(self):
        """
            Override Original method to allow quants in serial have more than one quantity in case of option
             Track serials in sales order only

        """
        for quant in self:
            if (quant.company_id and not quant.company_id.track_serial_sales_only) or quant.location_id.usage == 'customer':
                if float_compare(quant.quantity, 1,
                                 precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
                    raise ValidationError(_('A serial number should only be linked to a single product.'))
