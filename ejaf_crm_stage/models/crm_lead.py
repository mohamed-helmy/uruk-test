from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_set_lost(self, **additional_values):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('is_lost_stage', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 0, **additional_values})
        self._rebuild_pls_frequency_table_threshold()
        return True
