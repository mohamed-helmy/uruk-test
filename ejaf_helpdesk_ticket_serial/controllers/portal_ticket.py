# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.tools.translate import _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    @http.route([
        '/my/ticket/confirm/<int:ticket_id>',
        '/my/ticket/confirm/<int:ticket_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def ticket_confirm(self, ticket_id=None, access_token=None, **kw):
        try:
            ticket_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if ticket_sudo.stage_id.auto_change_to_stage_id:
            ticket_sudo.write({'stage_id':  ticket_sudo.stage_id.auto_change_to_stage_id.id})


            body = _('Ticket Confirmed by the customer')
            ticket_sudo.with_context(mail_create_nosubscribe=True).message_post(body=body, message_type='comment',
                                                                                subtype='mt_note')

        return request.redirect('/my/tickets')
