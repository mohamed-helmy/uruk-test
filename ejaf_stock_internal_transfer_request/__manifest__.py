# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Stock Internal Transfer Request',
    'depends': [
        'base',
        'stock',
        'ejaf_company_sequences',

    ],
    "description": """
   """,
    'author': "Ejaftech",

    'data': [
        'data/data.xml',
        'security/ir_categroy.xml',
        'security/groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizard/transfer_request_reason.xml',
        'views/internal_transfer_request.xml',
        'views/stock_picking.xml',
        'views/ir_config_views.xml',
        'views/delivery_method.xml',
    ],
    'installable': True,
    'application': False,
}
