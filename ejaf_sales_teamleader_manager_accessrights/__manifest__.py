# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Sales Teamleader Manager Accessrights',
    'depends': [
        'sale',
        'crm',
        'ejaf_multi_salesteamleader',

    ],
    "description": """
     Each sales team leader see all leads , pipelines,quotations of his team odoo app
    So create new Access Rights group "All Team Documents" under group sales
    2-add sales manger group to confirm sale order button
   """,
    'author': "Ejaftech",

    'data': [
        'security/groups.xml',
        'security/ir_rule.xml',
    ],
    'installable': True,
    'application': False,
}
