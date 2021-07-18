from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['brand_id'] = ', l.brand_id as brand_id'

        groupby += ', l.brand_id'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
