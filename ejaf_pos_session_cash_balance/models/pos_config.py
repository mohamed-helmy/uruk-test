# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosConfig(models.Model):

    _inherit = "pos.config"

    default_bank_stmt_cashbox_ids = fields.Many2many('account.bank.statement.cashbox', string='Default Cash Boxes', domain=[('is_a_template', '=', True)])