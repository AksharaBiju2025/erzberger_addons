from odoo import models

class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    def _get_default_pdf_report_id(self, move):
        if move.company_id.use_custom_sale_report:
            return self.env.ref(
                "erzberger_sale_report.action_report_invoice_custom"
            )

        return super()._get_default_pdf_report_id(move)