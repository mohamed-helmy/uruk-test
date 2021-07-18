# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Pass Contact In Product/Stock Move Reports',
    'depends': [
        'stock',
    ],
    "description": """
    pass contact field to stock move and stock move line .
   """,
    'author': "Ejaftech",

    'data': [
        'views/stock_move.xml',
        'views/stock_move_line.xml'
    ],
    'installable': True,
    'application': False,
}
