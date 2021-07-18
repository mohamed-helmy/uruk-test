# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Sales Subscription',
    'depends': [
        'base',
        'sale_subscription',

    ],
    "description": """
        This module adds the following:
        - update next recurring date to the last day in month if the start day is not the first day of month
    """,
    'author': "Ejaftech",

    'data': [

        'views/sale_subscription.xml',
    ],
    'installable': True,
    'application': False,
}
