from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    rfq = fields.Float(string="RFQ", compute='compute_rfq_qty')

    @api.depends('product_id')
    def compute_rfq_qty(self):
        for line in self:
            rfq = 0.0
            if line.product_id:
                product_orders_qty = self.sudo().search([('product_id', '=', line.product_id.id)]).filtered(lambda l:l.order_id.state == 'draft')
                rfq = sum(product_orders_qty.mapped('product_qty'))
            line.rfq = rfq
