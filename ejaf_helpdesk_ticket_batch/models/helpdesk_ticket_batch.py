# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)
TICKET_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]


class HelpDeskTicketBatc(models.Model):
    _name = 'helpdesk.ticket.batch'
    _rec_name = 'name'

    name = fields.Char(string="Name", copy=False, required=True)
    batch_date = fields.Date(string="Date", default=fields.Date.today)
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type")
    batch_type = fields.Selection([('customers', 'Customers'), ('serials', 'Serials')], string='Type',
                                  default='serials', required=True)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    user_id = fields.Many2one(comodel_name='res.users', string='Assign To')
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    customer_email = fields.Char(string="Customer Email", required=False, )

    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')],
                             default='draft')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Batch Name Already Exists !"),
    ]

    def open_batch_tickets_ids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'name': 'Batch Tickets',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('ticket_batch_id', '=', self.id)],
            'context': {
                'search_default_ticket_batch_id': self.id,
                'default_ticket_batch_id': self.id,
                'ticket_batch_id': self.id,
            }
        }
