# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_auto_change_stage = fields.Boolean(default=False, string="Change to another stage automatically?")
    auto_change_to_stage_id = fields.Many2one('helpdesk.stage', string="Automatically change to stage")
    auto_change_to_stage_days = fields.Integer("Number of days to change if idle", default=0)
    
    @api.model
    def process_auto_change_state(self):
        stage_ids = self.search([
            ('is_auto_change_stage', '=', True),
            ('auto_change_to_stage_id', '!=', False),
            ])
        for stage_id in stage_ids:
            self.env['helpdesk.ticket'].search([
                ('stage_id', '=', stage_id.ids),
                ('date_last_stage_update', '<=',  fields.Datetime.to_string(
                    datetime.now() - relativedelta(days=stage_id.auto_change_to_stage_days))),
                ]).write({
                    'stage_id': stage_id.auto_change_to_stage_id.id,
                    })
        return True
