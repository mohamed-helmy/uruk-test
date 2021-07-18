# -*- coding: utf-8 -*-
{
    'name': 'Manual Currency Rate',
    'category': 'Accounting/Accounting',
    'summary': 'Manual Currency Rate',
    'description': """
        This module allows to use manual currency rates in invoices/payments in currency conversion.
    """,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}