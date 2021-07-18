# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProductBrand(models.Model):
    _name = 'product.brand'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    team_ids = fields.Many2many('crm.team', string='Sales Team',
                                help="Link between Produc Brand and sales teams. When set, this limitate the current Product Brand to the selected sales teams.")
    user_id = fields.Many2one(comodel_name='res.users', string='Manager')
    team_users_ids = fields.Many2many(comodel_name='res.users', relation="crm_lead_team_users",
                                      compute='_compute_team_members', store=True)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Brand Name Already Exists!'),
    ]

    @api.depends('team_ids', 'team_ids.member_ids', 'team_ids.team_leader_ids', 'user_id')
    def _compute_team_members(self):
        for record in self:
            user_ids = []
            for member_ids in record.team_ids.mapped('member_ids'):
                user_ids.extend(member_ids.ids)
            if record.team_ids.mapped('team_leader_ids'):
                user_ids.extend(record.team_ids.mapped('team_leader_ids').ids)
            if record.user_id:
                user_ids.append(record.user_id.id)
            record.team_users_ids = False
            record.team_users_ids = [(6, 0, user_ids)]
