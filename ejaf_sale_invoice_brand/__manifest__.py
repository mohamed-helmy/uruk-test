# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Sales And Account Brand',
    'depends': [
        'base',
        'sale_management',
        'account',
        'ejaf_brand_management',

    ],
    "description": """add  brand to sale order line  and account invoice line and group by it.
   """,
    'author': "Ejaftech",

    'data': [

        'views/sale_report.xml',
        'views/account_invoice_report.xml'
    ],
    'installable': True,
    'application': False,
}
