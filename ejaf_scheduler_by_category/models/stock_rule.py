# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_moves_to_assign_domain(self):
        domain = super(ProcurementGroup, self)._get_moves_to_assign_domain()
        if self._context.get('prod_categ_ids', False) and self._context['prod_categ_ids']:
            domain += [('product_id.product_tmpl_id.categ_id', 'in', self._context.get('prod_categ_ids'))]
        return domain