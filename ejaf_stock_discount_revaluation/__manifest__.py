# -*- coding: utf-8 -*-
{
    'name': 'Stock Discount Revaluation',
    'category': 'Operations/Inventory',
    'summary': 'Stock Discount Revaluation',
    'description': """
This module allows you to easily add discounts on pickings and decide the split of these discount amounts among their stock moves in order to take them into account in your stock valuation.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['stock_landed_costs'],
    'data': [
        'data/stock_discount_revaluation_data.xml',
        'views/res_config_settings_views.xml',
        'views/stock_discount_revaluation_views.xml',
        'views/stock_valuation_layer_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}