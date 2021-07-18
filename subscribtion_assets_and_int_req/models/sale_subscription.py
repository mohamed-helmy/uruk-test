# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    asset_ids = fields.One2many(comodel_name="account.asset", inverse_name="sale_subscription_id")
    number_asset_ids = fields.Integer(compute="_compute_asset_ids")

    internal_transfer_request_ids = fields.One2many(comodel_name="internal.transfer.request",
                                                    inverse_name="sale_subscription_id")
    number_int_req_ids = fields.Integer(compute="_compute_internal_transfer_request_ids")


    @api.depends('internal_transfer_request_ids')
    def _compute_internal_transfer_request_ids(self):
        for record in self:
            record.number_int_req_ids = len(record.internal_transfer_request_ids)

    @api.depends('asset_ids')
    def _compute_asset_ids(self):
        for record in self:
            record.number_asset_ids = len(record.asset_ids)

    def create_fixed_asset(self):
        if not self.subscription_asset_product_ids:
            raise ValidationError(_("You must add at least one asset products to create assets"))
        for line in self.subscription_asset_product_ids:
            asset = self.env['account.asset'].create({
                'name': line.name,
                'model_id': line.model_id.id,
                'account_asset_id': line.model_id.account_asset_id.id,
                'account_depreciation_id': line.model_id.account_depreciation_id.id,
                'account_depreciation_expense_id': line.model_id.account_depreciation_expense_id.id,
                'journal_id': line.model_id.journal_id.id,
                'method': line.model_id.method,
                'method_number': line.model_id.method_number,
                'method_period': line.model_id.method_period,
                'method_progress_factor': line.model_id.method_progress_factor,
                'prorata': line.model_id.prorata,
                'prorata_date': line.model_id.prorata_date,
                'account_analytic_id': line.model_id.account_analytic_id.id,
                'analytic_tag_ids': [(6, 0, line.model_id.analytic_tag_ids.ids)],
                'sale_subscription_id': line.subscription_id.id,
                'state': 'draft',
                'asset_type': 'purchase',
            })
        return True

    def create_internal_request(self):
        if not self.subscription_asset_product_ids:
            raise ValidationError(_("You must add at least one asset products to create internal request"))

        if any(not line.product_id for line in self.subscription_asset_product_ids):
            raise ValidationError(_("You must add product to create internal request"))

        picking_type = self.env['stock.picking.type'].search([('company_id', '=', self.env.company.id),
                                                              ('code', '=', 'internal')],
                                                             limit=1)
        request_vals = {
            'user_id': self.user_id.id,
            'sale_subscription_id': self.id,
            'partner_id': self.partner_id.id,
        }
        request_line_ids = []
        for line in self.subscription_asset_product_ids:
            request_line_ids.append((0, 0, {'product_id': line.product_id.id,
                                            'description': line.name,
                                            'product_qty': 1,
                                            'uom_id': line.product_id.uom_id.id,
                                            'picking_type_id': picking_type.id,
                                            'location_id': picking_type.default_location_src_id.id ,
                                            'location_dest_id': picking_type.default_location_dest_id.id}))
        request_vals['request_line_ids'] = request_line_ids
        request = self.env['internal.transfer.request'].create(request_vals)
        return True

    def action_open_asset_ids(self):
        ret = {
            'name': _('Assets'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.asset_ids.ids)],
            'views': self.env['account.asset']._get_views('purchase'),
        }

        return ret

    def action_open_int_request_ids(self):
        ret = {
            'name': _('Internal Transfer Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'internal.transfer.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.internal_transfer_request_ids.ids)],
        }

        return ret