# -*- coding: utf-8 -*-
{
    'name': 'Product Details Barcode',
    'category': 'Operations/Inventory',
    'summary': 'Product Details Barcode',
    'description': """
        This module allows to scan product barcode to display product details.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'stock_barcode',
    ],
    'data': [
        'views/templates.xml',
        'views/client_action_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
        "static/src/xml/qweb_templates.xml",
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}
