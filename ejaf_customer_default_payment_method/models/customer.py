# -*- coding: utf-8 -*-
from odoo import models, fields


class Customer(models.Model):
    _inherit = 'res.partner'

    default_payment_method_id = fields.Many2one(comodel_name="account.journal",
                                                domain=[('type', 'in', ['cash', 'bank'])])
