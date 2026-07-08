# -*- coding: utf-8 -*-

from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # def action_print_delivery_custom(self):
    #     self.ensure_one()
    #
    #     if self.company_id.use_custom_sale_report:
    #         return self.env.ref(
    #             "erzberger_sale_report.action_report_delivery_note"
    #         ).report_action(self)
    #
    #     return self.env.ref(
    #         "stock.action_report_delivery"
    #     ).report_action(self)