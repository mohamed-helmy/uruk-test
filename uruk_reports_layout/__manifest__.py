# -*- coding: utf-8 -*-
{
    'name': 'Uruk Reports Layout',
    'depends': [

        'purchase', 'sale_stock','account','ejaf_sales_target','ejaf_company_decimal_accuracy'

    ],
    "description": """
   
   """,
    'author': "Ejaftech",

    'data': [
        'views/res_partner_bank_from_view.xml',
        'views/res_company.xml',
        'views/account_move.xml',
        'views/report_arabic_template.xml',
        'views/report_en_tempalate.xml',
        'views/sale_arabic_template.xml',
        'views/purchase_arabic_template.xml',
        'views/rfq_arabic_template.xml',
        'views/picking_arabic_template.xml',
        'views/delivery_slip_arabic_template.xml',
        'views/invoice_arabic_template.xml',
        'views/invoice_with_payment_arabic_template.xml',
        'views/stock_inventory_ar_report.xml',
        'views/en_invoice_report.xml',
        'views/usool_en_tempalate.xml',
        'views/usool_invoice_report.xml',
        'views/ejaf_english_invoice.xml',
        'views/ejaf_arabic_invoice.xml',
        'views/usool_ar_invoice_report.xml',
    ],
    'installable': True,
    'application': False,
}
