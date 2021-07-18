# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class PartnerTag(models.Model):
    _inherit = 'res.partner.category'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
