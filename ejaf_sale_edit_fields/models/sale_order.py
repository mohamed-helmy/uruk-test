from odoo import api, fields, models



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)],'request': [('readonly', False)]})
