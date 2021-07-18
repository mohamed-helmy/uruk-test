# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class IrActionsReportInherit(models.Model):
    _inherit = 'ir.actions.report'

    def render_qweb_pdf(self, res_ids=None, data=None):
        if res_ids and self.report_name == 'sale.report_saleorder' and not self.env.user.has_group('sales_team.group_sale_manager'):
            Model = self.env[self.model]
            record_ids = Model.browse(res_ids)
            for rec in record_ids:
                if rec.state in ['request']:
                    raise ValidationError(_('You have no access to print in current state.'))
        return super(IrActionsReportInherit, self).render_qweb_pdf(res_ids, data)