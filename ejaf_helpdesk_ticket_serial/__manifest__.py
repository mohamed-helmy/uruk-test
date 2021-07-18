# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Helpdesk Ticket with Serial',
    'depends': [
        'helpdesk_sale',
        'sale_stock',
        'sale_subscription',
        'helpdesk_stage_ticket_cron',

    ],
    "description": """
    Add to helpdesk ticket relation with serial number.
    Add also to sale subscription relation with serial number.   
   """,
    'author': "Ejaftech",
    'qweb': ['static/src/xml/*.xml'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/lot_view.xml',
        'views/ticket_view.xml',
        'views/product_view.xml',
        'views/sale_subscription_view.xml',
        'views/settings_view.xml',
        'views/ticket_portal_template.xml',
    ],
    'installable': True,
    'application': False,
}
