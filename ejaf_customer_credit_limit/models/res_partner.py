# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    allow_over_credit = fields.Boolean('Allow Over Credit?')
