from odoo import models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def _generate_template_attachments(self, res_ids, render_fields, render_results=None):
        """ Intercept automated attachment compiling to route to custom layout """
        # 1. Let the base method run its native execution loop
        render_results = super(MailTemplate, self)._generate_template_attachments(
            res_ids, render_fields, render_results=render_results
        )

        # 2. Check if we are handling a sale order and your company flag is checked
        if self.model == 'sale.order' and res_ids:
            orders = self.env['sale.order'].browse(res_ids)

            if any(order.company_id.use_custom_sale_report for order in orders):
                custom_report = self.env.ref('erzberger_sale_report.action_report_auftragsbestatigungs',
                                             raise_if_not_found=False)

                if custom_report:
                    for res_id in res_ids:
                        order = self.env['sale.order'].browse(res_id)

                        # Only modify if this specific order's company wants the custom report
                        if order.company_id.use_custom_sale_report:
                            import base64
                            from odoo.tools.safe_eval import safe_eval, time

                            # Render your custom report binary payload directly
                            report_content, report_format = self.env['ir.actions.report']._render_qweb_pdf(
                                custom_report, [res_id])
                            report_content = base64.b64encode(report_content)

                            # Determine the dynamic PDF document name
                            if custom_report.print_report_name:
                                report_name = safe_eval(custom_report.print_report_name,
                                                        {'object': order, 'time': time})
                            else:
                                report_name = 'Report'

                            extension = "." + report_format
                            if not report_name.endswith(extension):
                                report_name += extension

                            # Wipe out the standard default report attachment array element and enforce yours
                            if render_results and res_id in render_results:
                                render_results[res_id]['attachments'] = [(report_name, report_content)]

        return render_results