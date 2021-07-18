# -*- coding: utf-8 -*-
import json
import logging
from lxml import etree
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order',
                 'order_ids.company_id')
    def _compute_sale_data(self):
        super(CrmLead, self)._compute_sale_data()
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.order_ids:
                if order.state in ('request', 'draft', 'sent'):
                    quotation_cnt += 1
                if order.state not in ('request', 'draft', 'sent', 'cancel'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            lead.sale_amount_total = total
            lead.quotation_count = quotation_cnt
            lead.sale_order_count = sale_order_cnt

    def action_view_sale_quotation(self):
        action = super(CrmLead, self).action_view_sale_quotation()
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'in', ['request', 'draft', 'sent'])]
        return action

    def action_view_sale_order(self):
        action = super(CrmLead, self).action_view_sale_order()
        action['domain'] = [('opportunity_id', '=', self.id),
                            ('state', 'not in', ('request', 'draft', 'sent', 'cancel'))]
        return action


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('request', 'Draft'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='request')

    date_order = fields.Datetime(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    validity_date = fields.Date(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    require_signature = fields.Boolean(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    require_payment = fields.Boolean(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    partner_id = fields.Many2one(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    partner_invoice_id = fields.Many2one(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)],
                'sale': [('readonly', False)]})
    partner_shipping_id = fields.Many2one(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)],
                'sale': [('readonly', False)]})
    pricelist_id = fields.Many2one(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    analytic_account_id = fields.Many2one(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    commitment_date = fields.Datetime(
        states={'request': [('readonly', False)], 'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    can_approve = fields.Boolean(string='Can Approve', compute='check_approval_access')


    def check_approval_access(self):
        for rec in self:
            team_leaders = rec.team_id.team_leader_ids.ids if rec.team_id else False
            if self.env.user.has_group('sales_team.group_sale_manager') or (
                    team_leaders and self.env.user.id in team_leaders):
                rec.can_approve = True
            else:
                rec.can_approve = False

    def button_action_approve(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)
        doc = etree.XML(res['arch'])
        not_readonly_fields = ['warehouse_id']
        for field in res['fields']:
            for node in doc.xpath("//field[@name='%s']" % field):
                if node.get('name') not in not_readonly_fields:
                    node.set("readonly", "1")
                    modifiers = json.loads(node.get("modifiers"))
                    if 'readonly' in modifiers:
                        if isinstance(modifiers['readonly'], list):
                            if len(modifiers['readonly']):
                                domain = modifiers['readonly']
                                domain.insert(0, ['state', '!=', 'request'])
                                domain.insert(0, '|')
                                modifiers['readonly'] = domain
                            else:
                                modifiers['readonly'] = [('state', '!=', 'request')]
                        elif not modifiers['readonly']:
                            modifiers['readonly'] = [('state', '!=', 'request')]
                    else:
                        modifiers['readonly'] = [('state', '!=', 'request')]

                    node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
