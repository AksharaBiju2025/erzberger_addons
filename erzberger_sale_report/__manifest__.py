# -*- coding: utf-8 -*-
{
    'name': 'Erzberger Sale Order Report',
    'version': '19.0.1.0.0',
    'summary': 'Custom German Sale Order Report - Auftragsbestätigung',
    'description': """
        Custom Sale Order Report for Erzberger Verpackungssysteme.
        Generates a German-style Auftragsbestätigung (Order Confirmation)
        as a separate report action accessible from the Sale Order menu.
    """,
    'category': 'Sales',
    'author': 'Erzberger',
    'depends': ['sale', 'account'],
    'data': [
        'data/cron.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
        'report/sale_order_auftragsbestatigung_template.xml',
        'report/sale_order_auftragsbestatigung_report.xml',
        'report/delivery_slip_report.xml',
        'report/delivery_slip_template.xml',
        'report/invoice_report.xml',
        'report/invoice_template.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/res_company.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
