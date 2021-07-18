# -*- coding: utf-8 -*-
{
    'name': 'POS Session Cash Balance',
    'category': 'Point Of Sale',
    'summary': '',
    'description': """
           This module allows to consider all the cash registers in pos session cash balance calculations.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_session_views.xml',
        'views/pos_config_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}