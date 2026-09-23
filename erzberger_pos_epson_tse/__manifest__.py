# -*- coding: utf-8 -*-
{
    'name': "Erzberger POS - Epson TM-m30III USB TSE (Germany KassenSichV)",
    'summary': "Hardware TSE compliance for Epson TM-m30III with USB TSE Stick in Germany (BSI TR-03153)",
    'description': """
Erzberger POS - Epson TM-m30III USB TSE Integration (Germany KassenSichV)
========================================================================
Integrates Odoo 19 Point of Sale directly with the Epson TM-m30III receipt printer
equipped with the BSI-certified Epson USB TSE unit (TR-03153).

Key Features:
-------------
* 100% Offline Capable: Transaction signing directly via Epson ePOS-Device XML / TSE hardware interface.
* No Monthly Cloud Costs: Uses the 5-year certified hardware stick instead of cloud services.
* Legal Compliance: Fulfills German KassenSichV & BSI TR-03153 requirements:
  - startTransaction & finishTransaction cycle
  - Sequential transaction numbering & tamper-proof signature counters
  - Hash chaining & cryptographic signature (ecdsa-plain-SHA256)
  - Compliant receipt printing with audit data and QR-Code
* Test / Simulation Mode: Test and verify POS receipt flows even without the printer connected.
* Connection Diagnostic: Built-in ping and diagnostic tool in POS configuration.
    """,
    'version': '19.0.1.0.0',
    'category': 'Point of Sale/Localization',
    'author': 'Erzberger / Antigravity',
    'website': 'https://erzberger.de',
    'license': 'OEEL-1',
    'depends': [
        'point_of_sale',
        'l10n_de',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/res_config_settings_views.xml',
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'erzberger_pos_epson_tse/static/src/css/epson_tse_receipt.css',
            'erzberger_pos_epson_tse/static/src/app/utils/qrcode_generator.js',
            'erzberger_pos_epson_tse/static/src/app/services/epson_tse_service.js',
            'erzberger_pos_epson_tse/static/src/app/models/pos_order.js',
            'erzberger_pos_epson_tse/static/src/app/order_payment_validation/order_payment_validation.js',
            'erzberger_pos_epson_tse/static/src/app/components/order_receipt/order_receipt.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
