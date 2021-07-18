# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools.translate import html_translate


class AccountAccount(models.Model):
    _inherit = 'account.account'

    name = fields.Char(translate=True)
