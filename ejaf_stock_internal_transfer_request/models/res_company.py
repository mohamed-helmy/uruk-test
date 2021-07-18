# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import date, datetime
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    def create_sequence(self):
        self.ensure_one()
        if self != self.env.ref('base.main_company') and not self.created_seq:
            self.env['ir.sequence'].create({
                'name': 'Internal Transfer Request' + str(self.name),
                'code': 'internal.transfer.request',
                'padding': 4,
                'prefix': 'INT/Req/',
                'company_id': self.id
            })
        super(ResCompany, self).create_sequence()
