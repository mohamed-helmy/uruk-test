# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    created_seq = fields.Boolean(string="Created Seq", default=False)

    def create_sequence(self):
        """Override this method to create your desired sequences for the company"""
        self.ensure_one()
        if self != self.env.ref('base.main_company') and not self.created_seq:
            self.created_seq = True
