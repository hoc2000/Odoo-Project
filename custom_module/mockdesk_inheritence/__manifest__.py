# -*- coding: utf-8 -*-
{
    'name': "mockdesk_inheritence",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Hoc Vu",
    'sequence': 10,
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mock_desk'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/sale_order_view.xml',
        'views/helpdesk_customer_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
