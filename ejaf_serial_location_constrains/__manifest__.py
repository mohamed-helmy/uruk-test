# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Serial Location Constrains ',
    'depends': [
        'sale_stock',
        'ejaf_disable_track_serial',

    ],
    "description": """
            * Disable deliver or transfer any serial no. not in the source location of picking.
            * Disable users  create Receipt/Delivery order manual except admin user.
   """,
    'author': "Ejaftech",

    'data': [
    ],
    'installable': True,
    'application': False,
}
