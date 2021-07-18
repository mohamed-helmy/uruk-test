# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Brand Management',
    'depends': [
        'base',
        'sale_management',
        'ejaf_multi_salesteamleader',

    ],
    "description": """add product brand to sale module and teams for each Brand.
   """,
    'author': "Ejaftech",

    'data': [
        'security/ir.model.access.csv',
        'security/security_rule.xml',
        'views/product_brand.xml',
        'views/product_template.xml',
        'views/stock_quant.xml'
    ],
    'installable': True,
    'application': False,
}
