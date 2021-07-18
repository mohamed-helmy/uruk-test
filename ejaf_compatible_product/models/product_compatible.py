from odoo import api, fields, models



class ProductCompatible(models.Model):
    _name = 'product.compatible'

    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_tem_id = fields.Many2one(comodel_name="product.template")
    available_qty = fields.Float(string="Available qty", compute='compute_available_qty', readonly=True)

    @api.depends('product_id')
    def compute_available_qty(self):
        for line in self:
            if line.product_id:
                line.available_qty = line.product_id.qty_available
            else:
                line.available_qty = 0



