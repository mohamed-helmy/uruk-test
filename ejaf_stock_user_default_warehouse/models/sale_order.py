# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_warehouse_ids(self):
        warehouse_id = self.env.user.context_default_warehouse_id.id
        if not warehouse_id:
            warehouse_id = self.env['stock.warehouse'].search(
                [('company_id', '=', self.env.user.company_id.id)], limit=1)
        return warehouse_id

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", default=_default_warehouse_ids)

    @api.onchange('user_id')
    def onchange_user_warehouse_id(self):
        if self.user_id.context_default_warehouse_id:
            self.warehouse_id = self.user_id.context_default_warehouse_id
        else:
            self.warehouse_id = self.env['stock.warehouse'].search(
                [('company_id', '=', self.user_id.company_id.id)], limit=1)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        company = self.user_id.company_id or self.env.user.company_id
        if self.company_id == company:
            self.warehouse_id = self.env.user.context_default_warehouse_id.id
        else:
            self.warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
