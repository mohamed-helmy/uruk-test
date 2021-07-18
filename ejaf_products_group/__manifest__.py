# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Products Full Access Rights Group',
    'depends': [
        'product',
        'stock',
        'stock_account',
    ],
    "description": """
        This module 
            - Add group "Products Full Access Rights"
            - Restrict users in creating, editing or deleting product templates, 
        product variants, product attributes, and product attribute values.
   """,
    'author': "Ejaftech",

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}
