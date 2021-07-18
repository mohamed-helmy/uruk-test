# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools.translate import html_translate


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_not_decimal_accuracy = fields.Boolean(string="Not Decimal Accuracy", )
