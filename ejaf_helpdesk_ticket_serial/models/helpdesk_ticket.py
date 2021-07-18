# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sequence = fields.Char(string="Sequence", required=True, default="/")
    lot_id = fields.Many2one(comodel_name="stock.production.lot", string="Product Lot/Serial Number")
    lot_tag_id = fields.Many2one(comodel_name="lot.tag", string="Tag NO.")
    customer_location_id = fields.Many2one(comodel_name="res.partner", string="Customer Location",
                                           compute="_get_lot_sale_data")
    picking_id = fields.Many2one(comodel_name="stock.picking", string="Delivery Order",
                                 compute="_get_lot_sale_data")
    sold_date = fields.Date(string="Sold Date", compute="_get_lot_sale_data")
    warranty_date = fields.Date(string="Warranty End Date", compute="_get_lot_sale_data")
    effective_date = fields.Datetime(string="Effective Date", default=lambda self: fields.Datetime.now())
    service_contract_id = fields.Many2one(comodel_name="sale.subscription", string="Service Contract No.",
                                          compute="_get_lot_sale_data")
    solved_date = fields.Datetime(string="Solved Date")
    product_id = fields.Many2one(comodel_name="product.product", string="Product", related="lot_id.product_id", store=True)
    warranty_terms = fields.Text('Warranty Terms', related="product_id.warranty_terms", store=True)
    contract_expiry_date = fields.Date(string="Contract Expiry date", compute="_get_lot_sale_data")
    counter_reading_mono = fields.Integer(string="Counter Reading Mono")
    counter_reading_color = fields.Integer(string="Counter Reading Color")
    response_time = fields.Datetime(string="Response Time")
    sla_resolution_time = fields.Float(compute='_compute_sla_resolution_time', store=True, string="SLA Resolution Time")
    sla_response_time = fields.Float(compute='_compute_sla_response_time', store=True, string="SLA Response Time")

    @api.depends('effective_date', 'solved_date')
    def _compute_sla_resolution_time(self):
        for record in self:
            if record.solved_date and record.effective_date:
                dt = record.solved_date - record.effective_date
                record.sla_resolution_time = dt.days * 24 + dt.seconds / 3600  # Number of hours
            else:
                record.sla_resolution_time = 0

    @api.depends('effective_date', 'response_time')
    def _compute_sla_response_time(self):
        for record in self:
            if record.response_time and record.effective_date:
                dt = record.response_time - record.effective_date
                record.sla_response_time = dt.days * 24 + dt.seconds / 3600  # Number of hours
            else:
                record.sla_response_time = 0

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            self.lot_tag_id = self.lot_id.lot_tag_id

    @api.onchange('lot_tag_id')
    def onchange_lot_tag_id(self):
        if self.lot_tag_id:
            lot_id = self.env['stock.production.lot'].search([('lot_tag_id', '=', self.lot_tag_id.id)], limit=1)
            self.lot_id = lot_id.id

    @api.depends('lot_id')
    def _get_lot_sale_data(self):
        move_lines = self.env['stock.move.line']
        customer_location_id = False
        sold_date = False
        warranty_date = False
        picking_id = False
        service_contract_id = False
        sale_order_id = False
        partner_id = False
        contract_expiry_date = False
        for record in self:
            if record.lot_id:
                lot_move_lines = move_lines.search([('lot_id', '=', record.lot_id.id),
                                                    ('picking_code', '=', 'outgoing')], limit=1)
                if lot_move_lines:
                    move_id = lot_move_lines.move_id
                    customer_location_id = move_id.partner_id.id
                    picking_id = lot_move_lines.picking_id.id
                    if move_id.sale_line_id:
                        if move_id.sale_line_id.subscription_id and move_id.sale_line_id.subscription_id.is_service_contract:
                            service_contract_id = move_id.sale_line_id.subscription_id.id
                            contract_expiry_date = service_contract_id.date

                        sale_order_id = move_id.sale_line_id.order_id.id
                        partner_id = move_id.sale_line_id.order_id.partner_id.id
                        sold_date = move_id.sale_line_id.order_id.date_order
                        warranty_date = sold_date + timedelta(days=move_id.product_id.warranty_period)
                if not service_contract_id:
                    subscription_line_id = self.env['sale.subscription.serial.line'].sudo().search([('lot_id', '=', record.lot_id.id),
                                                                                 ('subscription_id.is_service_contract', '=', True)],
                                                                                limit=1)

                    service_contract_id = subscription_line_id.subscription_id.id
                    partner_id = subscription_line_id.subscription_id.partner_id.id
                    contract_expiry_date = subscription_line_id.subscription_id.date
            record.sale_order_id = sale_order_id
            record.sold_date = sold_date
            record.customer_location_id = customer_location_id
            record.warranty_date = warranty_date
            record.picking_id = picking_id
            record.service_contract_id = service_contract_id
            record.contract_expiry_date = contract_expiry_date
            record.partner_id = partner_id

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket.sequence')
        return super(HelpdeskTicket, self).create(vals)

