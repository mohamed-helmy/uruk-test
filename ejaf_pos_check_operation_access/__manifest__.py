# -*- coding: utf-8 -*-
{
    'name': 'POS Check Operation Type Access',
    'category': 'Sales/Point Of Sale',
    'summary': 'POS Check Operation Type Access',
    'description': """
This module checks the operation type access in pos.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['ejaf_pos_partial_payment_multi_currency', 'ejaf_location_managers'],
    'data': [
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/pos_multi_currency.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}