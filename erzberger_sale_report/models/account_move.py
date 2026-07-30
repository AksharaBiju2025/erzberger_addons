# -*- coding: utf-8 -*-

from odoo import models

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_pdf(self):
        self.ensure_one()

        if (
            self.company_id.use_custom_sale_report
            and self.move_type in ("out_invoice", "out_refund")
        ):
            return self.env.ref(
                "erzberger_sale_report.action_report_invoice_custom"
            ).report_action(self)

        return super().action_print_pdf()

    def preview_invoice(self):
        self.ensure_one()

        if (
            self.company_id.use_custom_sale_report
            and self.move_type in ("out_invoice", "out_refund")
        ):
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': self.get_portal_url(),
            }

        return super().preview_invoice()