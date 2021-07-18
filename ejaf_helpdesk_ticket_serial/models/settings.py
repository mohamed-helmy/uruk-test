

from odoo import api, fields, models, _


class Company(models.Model):
    _inherit = 'res.company'

    product_categ_id = fields.Many2one(comodel_name="product.category", string="Product Category")


class Config(models.TransientModel):
    _inherit = 'res.config.settings'

    product_categ_id = fields.Many2one(comodel_name="product.category", string="Product Category",
                                               related="company_id.product_categ_id", readonly=False)