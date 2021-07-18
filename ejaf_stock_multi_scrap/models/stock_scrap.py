# -*- coding: utf-8 -*-

import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    multi_scrap_id = fields.Many2one(comodel_name="stock.multi.scrap")
    analytic_tag_id = fields.Many2one(comodel_name="account.analytic.tag", related="multi_scrap_id.analytic_tag_id",
                                      store=True)

    def _prepare_move_values(self):
        self.ensure_one()
        result = super(StockScrap, self)._prepare_move_values()
        result['analytic_tag_id'] = self.analytic_tag_id.id
        return result


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_tag_id = fields.Many2one(comodel_name="account.analytic.tag")

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        self.ensure_one()
        result = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        # Add analytic tag
        for num in range(0, 2):
            if result[num][2]["account_id"] != self.product_id. \
                    categ_id.property_stock_valuation_account_id.id:
                result[num][2].update({
                    'analytic_tag_ids': [(6, 0, [self.analytic_tag_id.id])] if self.analytic_tag_id else False
                })

        return result
