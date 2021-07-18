# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, exceptions
from odoo import tools, _
from odoo.tools.translate import html_translate


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    vendor_quotation = fields.Char(string="Vendor Quotation")
