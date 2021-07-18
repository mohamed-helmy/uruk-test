# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Multi Sales team leaders',
    'category': 'POS',
    'description': """
This module adds Add max discount in POS Orders per user
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['point_of_sale'],
    'data': [
        'views/users_view.xml',
        'views/pos_templates.xml',
    ],
    'installable': True,
}