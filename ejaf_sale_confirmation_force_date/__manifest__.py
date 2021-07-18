# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Sale Confirmation Force Date (backdate)',
    'version': '13.0.1.0.0',
    'category': 'Sales',
    'depends': ['sale'],
    'description': """
        This module will allow you to force sale confirmation to a given date.
        """,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_confirmation_wizard.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
}
