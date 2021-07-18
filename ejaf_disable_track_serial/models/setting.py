# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    track_serial_sales_only = fields.Boolean(string="Track Serial in Sales Only")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    track_serial_sales_only = fields.Boolean(string="Track Serial in Sales Only",
                                             related="company_id.track_serial_sales_only",
                                             readonly=False)

    @api.onchange('group_stock_production_lot')
    def _onchange_group_stock_production_lot(self):
        super(ResConfigSettings, self)._onchange_group_stock_production_lot()
        if not self.group_stock_production_lot:
            self.track_serial_sales_only = False
