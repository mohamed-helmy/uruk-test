# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class LandedCostInherit(models.Model):
    _inherit = 'stock.landed.cost'

    is_stock_discount = fields.Boolean(string='Is Stock Discount?', copy='True')

    @api.constrains('cost_lines', 'cost_lines.discount_amount')
    def check_discount_amount(self):
        for rec in self:
            for line in rec.cost_lines:
                if float_compare(line.discount_amount, 0.0, 5) < 0:
                    raise ValidationError(_("Wrong value for discount amount, amount should be greater than or equal to 0."))

    def _default_account_journal_id(self):
        lc_journal = super(LandedCostInherit, self)._default_account_journal_id()

        # update journal with stock discount revaluation journal
        if self._context.get('default_is_stock_discount'):
            if self.env.company.sdr_journal_id:
                lc_journal = self.env.company.sdr_journal_id
            else:
                ir_property = self.env['ir.property'].search([
                    ('name', '=', 'property_stock_journal'),
                    ('company_id', '=', self.env.company.id)
                ], limit=1)
                if ir_property:
                    lc_journal = ir_property.get_by_record()
        return lc_journal

    @api.model
    def create(self, vals):
        # update sequence for stock discount revaluation
        if vals.get('name', _('New')) == _('New') and vals.get('is_stock_discount', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.discount.revaluation')
        return super(LandedCostInherit, self).create(vals)


class LandedCostLineInherit(models.Model):
    _inherit = 'stock.landed.cost.lines'

    discount_amount = fields.Float(string='Discount Amount')
    is_stock_discount = fields.Boolean(related='cost_id.is_stock_discount', store=True)

    # add default value to discount product
    def _default_product_id(self):
        sdr_product_id = self.env['product.product']
        if self._context.get('default_is_stock_discount') and self.env.company.sdr_product_id:
            sdr_product_id = self.env.company.sdr_product_id
        return sdr_product_id

    product_id = fields.Many2one('product.product', 'Product', required=True, default=lambda self: self._default_product_id())


    @api.constrains('discount_amount')
    def check_discount_amount(self):
        for rec in self:
            if float_compare(rec.discount_amount, 0.0, 5) < 0:
                raise ValidationError(_("Wrong value for discount amount, amount should be greater than or equal to 0."))

    @api.onchange('discount_amount', 'is_stock_discount')
    def onchange_discount_amount(self):
        if self.is_stock_discount:
            self.price_unit = - self.discount_amount