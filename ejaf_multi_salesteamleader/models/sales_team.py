# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    team_leader_ids = fields.Many2many("res.users", "team_leader_rel", "team_id", "leader_id", "Team Leaders")
    member_ids = fields.Many2many("res.users", "team_member_rel", "team_id", "member_id", "Team Members",
                                  domain=lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)]
                                  )
    user_id = fields.Many2one(comodel_name="res.users", string="Team Leader", compute="get_team_leader", store=True)

    @api.depends('team_leader_ids')
    def get_team_leader(self):
        for record in self:
            if record.team_leader_ids:
                record.user_id = record.team_leader_ids[0].id


class User(models.Model):
    _inherit = 'res.users'

    sales_team_ids = fields.Many2many("crm.team", "team_leader_rel", "leader_id", "team_id", string="Sales Teams of Leaders")
    team_member_ids = fields.Many2many("crm.team", "team_member_rel", "member_id", "team_id", string="Sales Teams of Members")
