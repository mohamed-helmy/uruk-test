# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Stage Ticket Cron',
    'depends': [
        'base',
        'helpdesk',

    ],
    "description": """Automatically stage tickets with configured duration.
   """,
    'author': "Ejaftech",

    'data': [
        
        # Security Files:

        # Data Files:
        'data/ir_cron.xml',
        
        # Menu items
        
        # Wizards Files:
        
        # Views Files:
        'views/helpdesk_stage.xml',
        
        # Templates Files:
        
    ],
    'installable': True,
    'application': False,
}
