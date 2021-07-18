# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class POApprovalLevel(models.Model):
    _name = 'po.approval.level'
    _description = 'PO Approval Levels'
    _order = 'sequence'


    name = fields.Char(string='Name', required=1)
    group_ids = fields.Many2many('res.groups', string='Groups', required=1)
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one('res.company', string='Company', required=1, ondelete='cascade',  default=lambda self: self.env.company.id)