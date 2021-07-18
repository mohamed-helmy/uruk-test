# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Stock Shipment',
    'depends': [
        'base',
        'purchase',
        'purchase_stock',
        'stock',
        'sales_team',
        'sale',


    ],
    "description": """
   """,
    'author': "Ejaftech",

    'data': [

        'views/stock_picking.xml',
        'views/purchase_order.xml',
        'views/product_move.xml',
    ],
    'installable': True,
    'application': False,
}
