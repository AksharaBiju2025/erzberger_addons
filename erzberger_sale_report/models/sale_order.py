# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    quotation_followup_sent = fields.Boolean(
        string="Follow-up Sent",
        default=False,
        copy=False
    )

    def action_print_custom(self):
        self.ensure_one()

        if self.company_id.use_custom_sale_report:
            return self.env.ref(
                "erzberger_sale_report.action_report_auftragsbestatigungs"
            ).report_action(self)

        return self.env.ref(
            "sale.action_report_saleorder"
        ).report_action(self)

    def _cron_quotation_followup(self):
        limit_date = fields.Datetime.now() - timedelta(minutes=1)

        quotations = self.search([
            ('state', '=', 'sent'),
            ('date_order', '<=', limit_date),
            ('quotation_followup_sent', '=', False),
        ])

        template = self.env.ref(
            "erzberger_sale_report.mail_template_quotation_followup",
            raise_if_not_found=False
        )

        if not template:
            return

        for quotation in quotations:

            if not quotation.user_id.email:
                continue
            _logger.info("EMAIL=%r", quotation.user_id.email)
            _logger.info("NAME=%r", quotation.user_id.name)
            template.send_mail(
                quotation.id,
                email_values={
                    "email_to": quotation.user_id.email
                },
                force_send=True
            )

            quotation.quotation_followup_sent = True