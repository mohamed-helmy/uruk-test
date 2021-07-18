# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from datetime import timedelta

_logger = logging.getLogger(__name__)


class SaleTargetLine(models.Model):
    _name = "sale.target.line"
    _description = "Sale Target Line"

    product_category_id = fields.Many2one(comodel_name="product.category", string="Category",
                                          required=False)
    sale_target_id = fields.Many2one(comodel_name="sale.target", required=True,
                                     ondelete="cascade")
    bonus_percent = fields.Float(string="Bonus Percentage")
    bonus_condition_from = fields.Float()
    bonus_condition_to = fields.Float()
    amount_achieved = fields.Float(compute="get_amount_achieved")
    achieved_percent = fields.Float(string="Achieve Perc(%)", compute="get_amount_achieved")
    bonus = fields.Float(string="Bonus", compute="get_amount_achieved")

    def get_amount_achieved(self):
        all_targets = self.mapped("sale_target_id")
        categories_amount_achieved_dict = all_targets._get_categories_amount_achieved()

        for record in self:
            amount_achieved = 0.0
            achieved_percent = 0.0
            bonus = 0.0
            matched_bonus_condition = 0.0

            if categories_amount_achieved_dict[record.sale_target_id.id].get(record.product_category_id.id):
                amount_achieved = categories_amount_achieved_dict[record.sale_target_id.id][record.product_category_id.id][0]
                matched_bonus_condition = categories_amount_achieved_dict[record.sale_target_id.id][record.product_category_id.id][1]

            if record.sale_target_id.target_amount:

                achieved_percent = (amount_achieved * 100) / record.sale_target_id.target_amount

            if matched_bonus_condition == record.bonus_condition_to :
                    bonus = (amount_achieved * record.bonus_percent) / 100

            record.amount_achieved = float(amount_achieved)
            record.achieved_percent = float(achieved_percent)
            record.bonus = float(bonus)
