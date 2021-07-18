# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Location Managers',
    'depends': [
        'base',
        'stock',
        'sale',

    ],
    "description": """
   """,
    'author': "Ejaftech",

    'data': [
        'security/groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/stock_location.xml',
        'views/res_users.xml',
        'views/sale_order.xml',
        'views/picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
