# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    context_default_warehouse_id = fields.Many2one('stock.warehouse', string='Sales person default warehouse',
                                                   company_dependent=True, )
