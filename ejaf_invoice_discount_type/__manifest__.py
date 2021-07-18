# -*- coding: utf-8 -*-
{
    'name': 'Invoice Discount Type',
    'category': 'Accounting/Accounting',
    'summary': 'Invoice Discount Type',
    'description': """
This module adds type (fixed, percentage) to invoice line discount.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['account'],
    'data': [
        'data/data.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}