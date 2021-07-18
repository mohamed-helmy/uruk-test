# -*- coding: utf-8 -*-
{
    'name': 'Subscriptions With Assets and Internal Request',
    'depends': [
        'sale_subscription',
        'account_asset',
        # 'ejaf_stock_internal_transfer_request',

    ],
    "description": """
    This module Add option to create assets from sale subscriptions
    also create internal request from sale subscriptions
   """,
    'author': "Ejaftech",

    'data': [
        'security/ir.model.access.csv',
        'views/sale_subscription.xml',
        'views/sale_view.xml',
        # 'views/asset_view.xml',
        # 'views/internal_request_view.xml',
    ],
    'installable': True,
    'application': False,
}
