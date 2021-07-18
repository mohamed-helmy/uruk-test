from odoo import fields, models, api, _
from odoo.exceptions import UserError



class SaleOrderline(models.Model):
    _inherit = "sale.order.line"

    is_mange_price = fields.Boolean(string="", compute='_compute_access_price')

    @api.depends('product_id')
    def _compute_access_price(self):
        for rec in self:
            if self.user_has_groups(
                    'ejaf_restrict_saleprice.groups_restrict_price_change'):
                rec.is_mange_price = True
            else:
                rec.is_mange_price = False
