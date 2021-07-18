# -*- coding: utf-8 -*-

import json

from lxml import etree

from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    team_id = fields.Many2one('crm.team', string='Team', default=_get_default_team, check_company=True,
                              domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(PurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                         submenu=submenu)
        # if context.get('params', False) and context['params'].get('id', False):  # Check for context value
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree']:
            for node in doc.xpath("//field"):  # All the view fields to readonly
                modifiers = json.loads(node.get('modifiers'))
                # node.set('readonly', '1')
                if 'readonly' in modifiers:
                    if isinstance(modifiers['readonly'], list):
                        if len(modifiers['readonly']):
                            domain = modifiers['readonly']
                            domain.insert(0, ['state', 'not in', ['draft', 'sent']])
                            domain.insert(0, '|')
                            modifiers.update({
                                'readonly': domain
                            })
                        else:
                            modifiers.update({
                                'readonly': ['state', 'not in', ['draft', 'sent']]
                            })
                    elif not modifiers['readonly']:
                        modifiers.update({
                            'readonly': ['state', 'not in', ['draft', 'sent']]
                        })
                else:
                    modifiers.update({
                        'readonly': ['state', 'not in', ['draft', 'sent']]
                    })
                node.set('modifiers', json.dumps(modifiers))
            res['arch'] = etree.tostring(doc)
        return res
