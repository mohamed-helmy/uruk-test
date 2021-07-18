# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        invoice_line_values = vals.get('invoice_line_ids', False)
        res = super(AccountMoveInherit, self).write(vals)
        for invoice in self:
            if invoice_line_values:
                for line in invoice_line_values:
                    line_values = line[2]
                    line_id = line[1]

                    if not line_values:
                        # there is no values
                        continue

                    # check new added fields
                    new_vals = {}
                    if line_values.get('discount_type', False):
                        new_vals['discount_type'] = line_values.get('discount_type')
                    if line_values.get('discount_amount', False):
                        new_vals['discount_amount'] = line_values.get('discount_amount')

                    if new_vals:
                        if isinstance(line_id, int):
                            # update values in invoice line if it was already created
                            invoice.invoice_line_ids.filtered(lambda x: x.id == line[1]).write(new_vals)
                        elif line_values.get('sequence', False):
                            # update values in invoice line using sequence
                            invoice.invoice_line_ids.filtered(lambda x: x.sequence == line_values.get('sequence')).write(new_vals)
        return res


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Type', default='percentage')
    discount_amount = fields.Float(string='Disc Amount')

    @api.onchange('discount_type', 'discount_amount', 'discount', 'quantity', 'price_unit', 'tax_ids')
    def onchange_discount_type(self):
        if self.discount_type == 'fixed':
            self.discount = 0.0
            self.discount = (self.discount_amount / (self.quantity * self.price_unit)) * 100 if (self.quantity * self.price_unit) else 0.0
        else:
            self.discount_amount = self.quantity * self.price_unit * (self.discount / 100.0)
