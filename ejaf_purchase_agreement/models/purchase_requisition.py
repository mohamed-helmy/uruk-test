# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import UserError

class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    requested_price = fields.Float(string="Requested Price")
