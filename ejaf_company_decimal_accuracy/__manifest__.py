# -*- coding: utf-8 -*-
{
    'name': "Ejaf Company Decimal Accuracy",
    'summary': """
       This module to customize reports for Company Decimal Accuracy """,
    'description': """
            This module to customize reports for Company Decimal Accuracy
    """,
    'author': "Ejaf Technology",
    'website': "http://www.ejaftech.com/",
    'version': '0.3',
    'depends': ['base','account','sale','purchase'],
    'data': [

        'views/res_company.xml',
        'report/invoice_report.xml',
        'report/quotations_report.xml',
        'report/purchase_order.xml',
        'report/purchase_qo.xml',

    ],
    'demo': [
    ],

}
