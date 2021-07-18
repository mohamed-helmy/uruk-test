from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _select(self):
        return super()._select() + ", line.brand_id as brand_id"

    def _group_by(self):
        return super()._group_by() + ", line.brand_id"
