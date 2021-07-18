# -*- coding: utf-8 -*-

from odoo import fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_batch_id = fields.Many2one(comodel_name="helpdesk.ticket.batch",string='Ticket Batch')
