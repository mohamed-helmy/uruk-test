# -*- coding: utf-8 -*-
{
    'name': 'Run Scheduler By Category',
    'category': 'Operations/Inventory',
    'summary': 'Run Scheduler By Category',
    'description': """
        This module allows to run operations scheduler by product category.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'stock',
    ],
    'data': [
        'wizard/stock_scheduler_compute_views.xml',
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
