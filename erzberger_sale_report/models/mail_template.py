import base64
from odoo import models
from odoo.tools.safe_eval import safe_eval, time


import logging
_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def _generate_template_attachments(self, res_ids, render_fields, render_results=None):
        render_results = super()._generate_template_attachments(
            res_ids, render_fields, render_results=render_results
        )

        if self.model != 'sale.order' or not res_ids:
            return render_results

        custom_report = self.env.ref(
            'erzberger_sale_report.action_report_auftragsbestatigungs',
            raise_if_not_found=False
        )
        if not custom_report:
            return render_results

        for res_id in res_ids:
            order = self.env['sale.order'].browse(res_id)
            _logger.info(
                "SO %s / company %s / use_custom_sale_report=%s",
                order.name, order.company_id.name, order.company_id.use_custom_sale_report
            )
            if order.company_id.use_custom_sale_report and res_id in render_results:
                report_content, report_format = self.env['ir.actions.report']._render_qweb_pdf(
                    custom_report, [res_id]
                )
                report_content = base64.b64encode(report_content)
                report_name = (
                    safe_eval(custom_report.print_report_name, {'object': order, 'time': time})
                    if custom_report.print_report_name else 'Report'
                )
                extension = "." + report_format
                if not report_name.endswith(extension):
                    report_name += extension
                render_results[res_id]['attachments'] = [(report_name, report_content)]

        return render_results