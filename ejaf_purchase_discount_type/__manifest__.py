# -*- coding: utf-8 -*-
{
    'name': 'Purchase Discount Type',
    'category': 'Operations/Purchase',
    'summary': 'Purchase Discount Type',
    'description': """
This module adds type (fixed, percentage) to purchase line discount.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['ejaf_invoice_discount_type', 'purchase'],
    'data': [
        'views/purchase_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}