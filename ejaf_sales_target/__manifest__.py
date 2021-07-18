# -*- coding: utf-8 -*-
{
    'name': 'Sales Target',
    'category': 'Sales/Sales',
    'summary': 'Sales Target and bonus',
    'description': """
        Add sales target achievement and bonus
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['sale_stock', 'sale_crm', 'point_of_sale'],
    'data': [
        'data/sequence.xml',
        'data/ir_cron.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/sale_target_views.xml',
        'views/sale_views.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}