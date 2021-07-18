# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmTag(models.Model):
    _inherit = 'crm.lead.tag'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
