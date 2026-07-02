# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    zpl_template = fields.Selection(
        selection_add=[
            ('erzberger_51x19', 'Erzberger (51mm x 19mm)'),
        ],
        ondelete={'erzberger_51x19': 'set default'},
    )