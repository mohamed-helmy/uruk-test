# -*- coding: utf-8 -*-
{
    'name': 'POS Partial Payment / Multi-Currency',
    'category': 'Sales/Point Of Sale',
    'summary': 'POS Partial Payment / Multi-Currency',
    'description': """
This module allows to partially pay the pos orders and to use multi-currency in order payment.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['point_of_sale'],
    'data': [
        'views/templates.xml',
        'views/pos_config_views.xml',
        'views/payment_method.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/pos_multi_currency.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}