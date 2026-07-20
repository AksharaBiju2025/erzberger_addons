# -*- coding: utf-8 -*-
{
    'name': 'Erzberger Customizations',
    'version': '19.0.1.0.0',
    'summary': 'Erzberger Customizations',
    'description': """
    """,
    'category': 'Sales',
    'author': 'Erzberger',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/product_template.xml',
        'report/product_templates.xml',
        ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
