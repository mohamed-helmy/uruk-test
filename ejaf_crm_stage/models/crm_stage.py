# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools.translate import html_translate


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    is_lost_stage = fields.Boolean(string=" Is Lost Stage")
