# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_show_available_qty = fields.Boolean(string="Show Available Qty in Src Location",
                                              implied_group='ejaf_stock_internal_transfer_request.group_show_available_qty')
