# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from itertools import groupby
from operator import itemgetter
from datetime import timedelta

_logger = logging.getLogger(__name__)


class SaleTarget(models.Model):
    _name = "sale.target"
    _description = "Sale Target"
    _inherit = 'mail.thread'

    STATE_LIST = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('canceled', 'Canceled'),
        ('closed', 'Closed'),
    ]

    name = fields.Char(required=True, track_visibility='onchange', default='/', copy=False)
    state = fields.Selection(STATE_LIST, required=True, readonly=True,
                             default='draft', string="Status", track_visibility='onchange')
    company_id = fields.Many2one(comodel_name="res.company", default=lambda self: self.env.company)
    sales_person_id = fields.Many2one(comodel_name="res.users")
    start_date = fields.Date(copy=False)
    end_date = fields.Date(copy=False)
    target_achieve_type = fields.Selection(string="Target Achieve",
                                           selection=[('sale_order_confirmed', 'Sale Order Confirmed'),
                                                      ('delivery_order_done', 'Delivery Order Done'),
                                                      ('invoice_validated', 'Invoice Validated'),
                                                      ('invoice_paid', 'Invoice Paid'),
                                                      ('journal_item', 'Journal Items'),
                                                      ('pos_orders', 'POS Orders'),
                                                      ],
                                           required=True)
    enable_crm_only = fields.Boolean(string="Enable Achievements from CRM Only")
    target_amount = fields.Float()
    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible",
                                     default=lambda self: self.env.user)
    total_achievement = fields.Float(compute="get_amount_achieved")
    achievement_percent = fields.Float(compute="get_amount_achieved")
    difference = fields.Float(compute="get_amount_achieved")
    line_ids = fields.One2many(comodel_name="sale.target.line", inverse_name="sale_target_id",
                               copy=True)
    active = fields.Boolean('Active', default=True)

    @api.constrains('enable_crm_only', 'target_achieve_type')
    def _check_target_achieve_type(self):
        for record in self:
            if record.target_achieve_type == 'pos_orders' and record.enable_crm_only:
                raise ValidationError(_("You cant Enable Achievements from CRM Only with POS Orders  Target achieve"))

    @api.constrains('start_date', 'end_date', 'sales_person_id', 'company_id')
    def _check_date(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError(_("End date must be bigger than start date"))
            domain = [
                ('sales_person_id', '=', record.sales_person_id.id),
                ('id', '!=', record.id),
                ('state', '!=', 'canceled'),
                ('company_id', '=', record.company_id.id),
            ]
            targets = self.search(domain)
            if record.start_date and record.end_date:
                overlap_targets = targets.filtered(lambda t: t.start_date and t.end_date and (
                                                            (t.start_date <= record.start_date <= t.end_date)
                                                             or (t.start_date <= record.end_date <= t.end_date)))
                if len(overlap_targets) > 0:
                    raise ValidationError(
                        _('Targets start and end date should not overlap pre-existing ones. It overlaps "{}" '.format(
                            overlap_targets.mapped('name'))))

    def get_amount_achieved(self):
        total_achievement = 0.0
        achievement_percent = 0.0
        difference = 0.0
        for record in self:
            if record.line_ids and record.state != 'canceled':
                unique_categories = []
                total_achievement = 0.0
                for line in record.line_ids:
                    if line.product_category_id.id not in unique_categories:

                        total_achievement += line.amount_achieved
                        unique_categories.append(line.product_category_id.id)

                difference = total_achievement - record.target_amount
                if record.target_amount:
                    achievement_percent = (total_achievement * 100) / record.target_amount
            record.total_achievement = total_achievement
            record.achievement_percent = achievement_percent
            record.difference = difference

    def action_confirm(self):
        for record in self:
            if record.target_amount <= 0.0:
                raise ValidationError(_("You cant confirm without target amount"))

            if not record.line_ids:
                raise ValidationError(_("You cant confirm without lines"))
            if any(line.bonus_condition_from <= 0.0 for line in record.line_ids) or \
                any(line.bonus_condition_to <= 0.0 for line in record.line_ids):
                    raise ValidationError(_("You cant confirm lines with no bonus condition from/to"))

            if any(line.bonus_percent <= 0.0 for line in record.line_ids):
                raise ValidationError(_("You cant confirm lines with no bonus Percentage"))

            if record.target_achieve_type != 'invoice_paid' and any(not line.product_category_id for line in record.line_ids):
                raise ValidationError(_("You cant confirm lines with no Product Category"))
            record.state = 'open'
            record.name = self.env['ir.sequence'].next_by_code('sale.target')

    def action_cancel(self):
        for record in self:
            record.state = 'canceled'

    def close_sale_target(self,):
        for target in self.env['sale.target'].search([('end_date', '<=', fields.Date.today()),
                                                      ('state', 'not in', ['closed', 'canceled'])]):
            target.state = 'closed'
        return True

    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a Confirmed Record! Try to cancel it before.'))
        return super(SaleTarget, self).unlink()


    def _get_categories_amount_achieved(self):
        """
        return for each category amount achieved and matched line for bonus
        """
        res = {}
        for target in self:
            res[target.id] = {}
            if target.state != 'cancel' and target.end_date and target.start_date:
                categories = target.line_ids.mapped('product_category_id')
                date_to = fields.Datetime.from_string(target.end_date) + timedelta(hours=23, minutes=59)
                for category in categories:
                    sale_order_lines = self.env['sale.order.line'].sudo().search(
                        [('product_id.categ_id', 'child_of', category.id),
                         ('salesman_id', '=', target.sales_person_id.id),
                         ('order_id.date_order', '>=', target.start_date),
                         ('order_id.date_order', '<=', date_to),
                         ('company_id', '=', target.company_id.id)])

                    if target.enable_crm_only:
                        sale_order_lines = sale_order_lines.filtered(lambda s: s.order_id.opportunity_id)

                    if target.target_achieve_type == 'sale_order_confirmed':
                        confirmed_sales = sale_order_lines.filtered(lambda l: l.state in ['sale', 'done'])

                        amount_achieved = sum(confirmed_sales.mapped('price_subtotal'))

                    elif target.target_achieve_type == 'delivery_order_done':
                        done_deliveries = sale_order_lines.mapped('move_ids').filtered(lambda m: m.state == 'done'
                                                                                                 and fields.Datetime.from_string(
                            target.start_date) <= m.date <= fields.Datetime.from_string(date_to))
                        matched_sale_lines = done_deliveries.mapped('sale_line_id')
                        amount_achieved = sum(matched_sale_lines.mapped('qty_delivered_amount'))

                    elif target.target_achieve_type == 'invoice_validated':
                        invoice_validated = sale_order_lines.mapped('invoice_lines').filtered(
                            lambda v: v.parent_state == 'posted'
                                      and target.start_date <= v.move_id.invoice_date <= target.end_date)

                        amount_achieved = sum(invoice_validated.mapped('price_subtotal'))
                    elif target.target_achieve_type == 'journal_item':

                        invoice_validated = sale_order_lines.mapped('invoice_lines').filtered(
                            lambda v: v.parent_state == 'posted'
                                      and target.start_date <= v.move_id.invoice_date <= target.end_date)
                        amount_achieved = abs(sum(invoice_validated.mapped('balance')))

                    elif target.target_achieve_type == 'invoice_paid':
                        invoice_paid = sale_order_lines.mapped('invoice_lines') \
                            .filtered(lambda v: v.move_id.invoice_payment_state == 'paid' and
                                                target.start_date <= v.move_id.invoice_date <= target.end_date)

                        amount_achieved = sum(invoice_paid.mapped('price_subtotal'))

                    else:
                        pos_orders = self.env['pos.order.line'].sudo().search(
                            [('product_id.categ_id', 'child_of', category.id),
                             ('order_id.user_id', '=', target.sales_person_id.id),
                             ('order_id.state', '!=', 'cancel'),
                             ('order_id.date_order', '>=', target.start_date),
                             ('order_id.date_order', '<=', date_to),
                             ('company_id', '=', target.company_id.id)])

                        amount_achieved = sum(pos_orders.mapped('price_subtotal'))
                    matched_bonus_line = target.line_ids.filtered(lambda l: l.product_category_id.id == category.id and
                                                                 (l.bonus_condition_to >= amount_achieved >= l.bonus_condition_from  or amount_achieved > l.bonus_condition_to))

                    max_bonus = max(matched_bonus_line.mapped("bonus_condition_to") or [0.0])

                    res[target.id][category.id] = [amount_achieved, max_bonus]
        return res