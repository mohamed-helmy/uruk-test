# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Default Stock Warehouse on User',
    'summary': 'Configure a default warehouse on user',
    'description': """Default Warehouse on User With this module, 
    you will be able to configure a default warehouse in the preferences of the user.
    """,
    'author': "Ejaftech",
    'depends': ['base', 'stock', 'sale','sale_stock','ejaf_location_managers'],

    'data': [

        'views/res_users_view.xml',
    ],

    'installable': True,
}
