# -*- coding: utf-8 -*-
{
    'name': 'Sales Customization',
    'category': 'Sales/Sales',
    'summary': 'Sales Customization',
    'description': """
        This module adds the following:
            - new state draft in SO
            - update access on SO
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['sale', 'sales_team', 'sale_crm', 'ejaf_sales_teamleader_manager_accessrights'],
    'data': [
        'views/sale_views.xml',
        'views/product_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}