# -*- coding: utf-8 -*-
from odoo import fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    epson_tse_start_counter = fields.Integer(
        string="TSE Start Signature Counter",
        readonly=True,
        copy=False,
        help="TSE signature counter at the beginning of the POS session."
    )
    epson_tse_end_counter = fields.Integer(
        string="TSE End Signature Counter",
        readonly=True,
        copy=False,
        help="TSE signature counter at the closing of the POS session."
    )
    epson_tse_total_signed_orders = fields.Integer(
        string="Total TSE Signed Orders",
        compute='_compute_epson_tse_stats',
        store=True
    )

    def _compute_epson_tse_stats(self):
        for session in self:
            session.epson_tse_total_signed_orders = len(
                session.order_ids.filtered(lambda o: o.epson_tse_status == 'signed')
            )
