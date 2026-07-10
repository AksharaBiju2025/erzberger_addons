from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        # Intercept calls to the default sale order report
        if report_ref == 'sale.action_report_saleorder' and res_ids:
            orders = self.env['sale.order'].browse(res_ids)

            # Check if any of the processed orders belong to a company using the custom report
            if any(order.company_id.use_custom_sale_report for order in orders):
                report_ref = 'erzberger_sale_report.action_report_auftragsbestatigungs'

        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)