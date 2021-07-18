# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class InternalTransferRequest(models.Model):
    _name = 'internal.transfer.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default='/', readonly=True, copy=False)
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
                             default='draft', track_visibility='onchange')
    date = fields.Date(string="Date", default=fields.Date.context_today)
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible", required=True,
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", index=True, default=lambda self: self.env.company)
    request_line_ids = fields.One2many(comodel_name="transfer.request.line", inverse_name="internal_request_id")
    delivery_method_id = fields.Many2one(comodel_name="delivery.method", string="Delivery Method")
    estimated_cost = fields.Float(string="Estimated Cost")
    reject_reason = fields.Text(string="Reject Reason")

    def _check_lines_for_submit(self):
        if not self.request_line_ids:
            raise ValidationError(_("You must add at least one line from Operation"))

    def _create_stock_moves(self, move_line_values_list, picking):
        moves = self.env['stock.move']
        for values in move_line_values_list:
            values['picking_id'] = picking.id
            move = self.env['stock.move'].create(values)
        return True

    def create_internal_transfer(self):
        self._check_lines_for_submit()
        stock_picking_obj = self.env['stock.picking']
        is_transferred = False
        grouped_operation_types = self.request_line_ids.mapped('picking_type_id')
        for operation_type in set(grouped_operation_types):
            move_line_vals = []
            matched_lines = self.request_line_ids.filtered(lambda l: l.picking_type_id.id == operation_type.id)
            picking_request_vals = {
                'internal_request_id': self.id,
                'company_id': self.company_id.id,
                'is_transit_stage': True,
                'partner_id': self.partner_id.id,
                'user_id': self.user_id.id,
                'picking_type_id': operation_type.id,
                'location_id': matched_lines[0].location_id.id,
                'location_dest_id': matched_lines[0].location_dest_id.id,
            }
            for line in matched_lines:
                move_line_vals.append({
                    'name': self.name or line.description,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.uom_id.id,
                    'description_picking': line.description,
                    'date_expected': fields.Datetime.now(),
                    'location_id':line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,

                })

            # picking_request_vals.update({'move_ids_without_package': request_line_ids})
            transfer = stock_picking_obj.sudo().create(picking_request_vals)
            moves = self._create_stock_moves(move_line_vals, transfer)

            if transfer:
                is_transferred = True
        if is_transferred:
            self.state = 'approved'
        return True

    def action_submit(self):
        self._check_lines_for_submit()

        self.state = 'submit'
        return True

    def action_reject_request(self):
        self.ensure_one()
        return {
            'name': _('Reject Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'transfer.request.reason',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' or not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('internal.transfer.request')
            print(vals,'kkkkk')
        return super(InternalTransferRequest, self).create(vals)

    def open_internal_transfer_ids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'name': 'Internal transfer',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('internal_request_id', '=', self.id)],
            'context': {
                'search_default_internal_request_id': self.id,
                'default_picking_request_id': self.id,
                'internal_request_id': self.id,
            }
        }


class TransferRequestLine(models.Model):
    _name = 'transfer.request.line'

    @api.model
    def _default_picking_type_id(self):
        company = self.env.company.id
        picking_type = self.env['stock.picking.type'].search([('company_id', '=', company), ('code', '=', 'internal')],
                                                             limit=1)
        return picking_type.id

    product_id = fields.Many2one(comodel_name="product.product", string="product", required=True)
    description = fields.Text(string="Description")
    product_qty = fields.Float(string="Qty", required=True)
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure", required=True)
    available_qty = fields.Float(string="Available Qty", compute='compute_available_qty')
    location_id = fields.Many2one('stock.location', "Source Location", required=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location", required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, check_company=True,
                                      default=_default_picking_type_id)
    notes = fields.Text(string="Note")
    internal_request_id = fields.Many2one(comodel_name="internal.transfer.request",string='Stock Request')
    state = fields.Selection(related='internal_request_id.state', store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.uom_id = line.product_id.uom_id
                line.description = line.product_id.description_picking or line.product_id.description

    @api.onchange('picking_type_id')
    def _onchange_picking_type(self):
        for line in self:
            if line.picking_type_id:
                line.location_id = line.picking_type_id.default_location_src_id.id
                line.location_dest_id = line.picking_type_id.default_location_dest_id.id

    @api.constrains('product_qty')
    def _check_product_qty(self):
        for line in self:
            product_qty = line.product_qty
            if product_qty <= 0:
                raise ValidationError(_("Product Qty Must be greater than Zero."))

    @api.depends('location_id', 'product_id')
    def compute_available_qty(self):
        for line in self:
            available_quantity = self.env['stock.quant']._get_available_quantity(line.product_id,
                                                                                 line.location_id,
                                                                                 allow_negative=True)
            line.available_qty = available_quantity
