# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        p = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for quant in self:
            if quant.company_id and not quant.company_id.track_serial_sales_only:

                if (float_compare(quant.quantity, 0, precision_digits=p) == -1
                    and quant.product_id.type == "product"
                    and quant.location_id.usage in ["internal", "transit"]):
                    msg_add = ""
                    if quant.lot_id:
                        msg_add = (_(" with lot '%s'") % quant.lot_id.name_get()[0][1])
                    raise ValidationError(
                        _(
                            """You cannot validate this stock operation for product %s %s because the negative stock is 
                            not allowed """
                        )
                        % (
                            quant.product_id.name,
                            msg_add,
                        )
                    )
