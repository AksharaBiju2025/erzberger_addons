from odoo import http
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.http import request


class CustomerPortalInherit(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None,
                           message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except Exception:
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            report_ref = (
                'erzberger_sale_report.action_report_auftragsbestatigungs'
                if order_sudo.company_id.use_custom_sale_report
                else 'sale.action_report_saleorder'
            )
            return self._show_report(
                model=order_sudo,
                report_type=report_type,
                report_ref=report_ref,
                download=download,
            )

        return super().portal_order_page(
            order_id, report_type=report_type, access_token=access_token,
            message=message, download=download, **kw
        )

    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access('account.move', invoice_id, access_token=access_token)
        except Exception:
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            if (
                invoice_sudo.company_id.use_custom_sale_report
                and invoice_sudo.move_type in ('out_invoice', 'out_refund')
            ):
                return self._show_report(
                    model=invoice_sudo,
                    report_type=report_type,
                    report_ref='erzberger_sale_report.action_report_invoice_custom',
                    download=download,
                )

        return super().portal_my_invoice_detail(
            invoice_id, access_token=access_token, report_type=report_type, download=download, **kw
        )