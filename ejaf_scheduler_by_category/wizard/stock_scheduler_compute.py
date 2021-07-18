# -*- coding: utf-8 -*-

from odoo import models, fields


class StockSchedulerCompute(models.TransientModel):
    _inherit = 'stock.scheduler.compute'

    categ_ids = fields.Many2many('product.category', string='Product Categories')

    def procure_calculation_by_categ(self):
        return self.with_context(prod_categ_ids=self.categ_ids.ids).procure_calculation()
