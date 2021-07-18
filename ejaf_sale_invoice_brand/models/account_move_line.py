from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    brand_id = fields.Many2one(related='product_id.brand_id', comodel_name="product.brand", string="Brand", store=True)
