# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    pos_max_discount = fields.Float()