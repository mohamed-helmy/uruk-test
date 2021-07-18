# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Mult Companies Rules',
    'depends': [
        'base',
        'sale_stock',
        'account_accountant',
        'pos_sale',
        'crm'
    ],
    "description": """
    ADD multi company rules for these objects:
    1.Product Categories
    2.Analytic Accounts/Tags
   """,
    'author': "Ejaftech",

    'data': [
        'security/rules.xml',
        'views/product_category_views.xml',
        'views/crm_tag_view.xml',
        'views/account_tag_view.xml',
        'views/view_partner_category.xml'
    ],
    'installable': True,
    'application': False,
}
