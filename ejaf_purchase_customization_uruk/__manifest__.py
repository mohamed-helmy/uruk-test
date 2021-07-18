# -*- coding: utf-8 -*-
{
    'name': 'Purchase Customization',
    'category': 'Operations/Purchase',
    'summary': 'Purchase Customization',
    'description': """
        This module adds the following:
            - make po fields readonly after first level approval.
            - add Team field in purchase.
            - add new access group called "All Team Document".
            - each user read his own purchase orders for his team.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['ejaf_purchase_multi_approval', 'sales_team'],
    'data': [
        'security/security.xml',
        'views/purchase_order.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
