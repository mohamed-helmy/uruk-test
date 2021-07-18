# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Helpdesk ticket Batch ',
    'depends': [
        'ejaf_helpdesk_ticket_serial',

    ],
    "description": """
    Generate batch of tickets with serials or partners 
   """,
    'author': "Ejaftech",

    'data': [
        'security/ir.model.access.csv',
        'wizard/helpdesk_ticket_batch_wizard.xml',
        'views/helpdesk_ticket.xml',
        'views/helpdesk_ticket_batch.xml',
    ],
    'installable': True,
    'application': False,
}
