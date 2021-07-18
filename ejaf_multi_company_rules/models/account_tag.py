# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountTag(models.Model):
    _inherit = 'account.account.tag'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)