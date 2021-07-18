# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HelpdesckTicketWizard(models.TransientModel):
    _name = "helpdesck.ticket.wizard"

    partner_ids = fields.Many2many("res.partner")
    serial_ids = fields.Many2many("stock.production.lot")
    batch_id = fields.Many2one("helpdesk.ticket.batch")
    batch_type = fields.Selection([('customers', 'Customers'), ('serials', 'Serials')])

    def compute_sheet(self):
        tickets = self.env['helpdesk.ticket']
        if self.batch_type == 'customers':
            if not self.partner_ids:
                raise UserError(_("You must select Customer(s) to generate Ticket(s)."))
            for partner in self.partner_ids:
                res = {
                    'ticket_batch_id': self.batch_id.id,
                    'name': str(self.batch_id.name + '/' or '') + str(partner.name or ''),
                    'partner_id': partner.id,
                    'ticket_type_id': self.batch_id.ticket_type_id.id,
                    'priority': self.batch_id.priority,
                    'partner_email': self.batch_id.customer_email,
                    # 'partner_id': self.batch_id.partner_id.id,
                    'user_id': self.batch_id.user_id.id,

                }
                self.env['helpdesk.ticket'].create(res)
                self.batch_id.state = 'confirmed'

        if self.batch_type == 'serials':
            if not self.serial_ids:
                raise UserError(_("You must select Serial(s) to generate Ticket(s)."))
            for serial in self.serial_ids:
                res = {
                    'ticket_batch_id': self.batch_id.id,
                    'name': str(self.batch_id.name + '/' or '') + str(serial.name or ''),
                    'lot_id': serial.id,
                    'ticket_type_id': self.batch_id.ticket_type_id.id,
                    'priority': self.batch_id.priority,
                    'partner_email': self.batch_id.customer_email,
                    'partner_id': self.batch_id.partner_id.id,
                    'user_id': self.batch_id.user_id.id,

                }
                self.env['helpdesk.ticket'].create(res)
                self.batch_id.state = 'confirmed'

        return {'type': 'ir.actions.act_window_close'}
