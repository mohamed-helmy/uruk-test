# -*- coding: utf-8 -*-
{
    'name': "Ejaf Multi Scarp Orders",
    'summary': """
       This module allows you to create multiple Scrap Orders on a single click """,
    'description': """
      create multiple Scrap Orders on a single click
    """,

    'author': "Ejaf Technology",
    'website': "http://www.ejaftech.com/",


    'category': 'New App',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base' , 'stock_account'],

    # always loaded
    'data': [

        'security/ir_categroy.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/stock_multi_scrap.xml',
        'views/stock_scrap_views.xml',
        'reports/report.xml',
        'reports/report_multi_scrap.xml',
        'data/ir_sequence_data.xml',




    ],
    # only loaded in demonstration mode

}