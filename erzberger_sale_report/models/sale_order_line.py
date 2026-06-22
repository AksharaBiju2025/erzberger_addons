# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from datetime import timedelta
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    reorder_reminder_6_sent = fields.Boolean(default=False)
    reorder_reminder_12_sent = fields.Boolean(default=False)
    reorder_reminder_15_sent = fields.Boolean(default=False)
    reorder_reminder_18_sent = fields.Boolean(default=False)


    def _cron_reorder_followup(self):

        today = fields.Date.today()

        lines = self.env['sale.order.line'].search([
            ('order_id.state', 'in', ['sale', 'done']),
        ])

        for line in lines:

            order_date = line.order_id.date_order.date()

            next_orders = self.env['sale.order.line'].search_count([
                ('id', '!=', line.id),
                ('product_id', '=', line.product_id.id),
                ('order_id.partner_id', '=', line.order_id.partner_id.id),
                ('order_id.state', 'in', ['sale', 'done']),
                ('order_id.date_order', '>', line.order_id.date_order),
            ])

            if next_orders:
                continue

            age_months = (
                (today.year - order_date.year) * 12
                + (order_date.month - today.month)
            )

            if age_months == 6 and not line.reorder_reminder_6_sent:
                self._send_reorder_mail(line, 6)
                line.reorder_reminder_6_sent = True

            if age_months == 12 and not line.reorder_reminder_12_sent:
                self._send_reorder_mail(line, 12)
                line.reorder_reminder_12_sent = True

            if age_months == 15 and not line.reorder_reminder_15_sent:
                self._send_reorder_mail(line, 15)
                line.reorder_reminder_15_sent = True

            if age_months == 18 and not line.reorder_reminder_18_sent:
                self._send_reorder_mail(line, 18)
                line.reorder_reminder_18_sent = True

    def _send_reorder_mail(self, line, months):

        template = self.env.ref(
            "erzberger_sale_report.mail_template_reorder_remainder",
            raise_if_not_found=False
        )

        if not template:
            return None

        template.send_mail(
            line.id,
            email_values={
                "email_to": line.order_id.partner_id.email,
            },
            force_send=True,
        )