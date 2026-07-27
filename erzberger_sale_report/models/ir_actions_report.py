from odoo import models
import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from pypdf import PdfReader, PdfWriter
from pypdf import PdfReader, PdfWriter, Transformation



class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    # def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
    #     # Intercept calls to the default sale order report
    #     if report_ref == 'sale.action_report_saleorder' and res_ids:
    #         orders = self.env['sale.order'].browse(res_ids)

    #         # Check if any of the processed orders belong to a company using the custom report
    #         if any(order.company_id.use_custom_sale_report for order in orders):
    #             report_ref = 'erzberger_sale_report.action_report_auftragsbestatigungs'

    #     return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
    
    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        # Intercept calls to the default sale order report
        if report_ref == 'sale.action_report_saleorder' and res_ids:
            orders = self.env['sale.order'].browse(res_ids)

            # Check if any of the processed orders belong to a company using the custom report
            if any(order.company_id.use_custom_sale_report for order in orders):
                report_ref = 'erzberger_sale_report.action_report_auftragsbestatigungs'

        pdf_content, pdf_type = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        if pdf_type != "pdf" or not res_ids:
            return pdf_content, pdf_type

        wm_text = "Die Marke aus dem Erzgebirge !     "

        reader = PdfReader(io.BytesIO(pdf_content))
        writer = PdfWriter()

        page_w = float(reader.pages[0].mediabox.width)
        page_h = float(reader.pages[0].mediabox.height)

        # Distance from the right edge to the text baseline (points).
        right_offset = 10

        overlay_buf = io.BytesIO()
        c = canvas.Canvas(overlay_buf, pagesize=(page_w, page_h))
        c.saveState()
        c.translate(page_w - right_offset, page_h / 2)
        c.rotate(90)
        c.setFont("Helvetica-Bold", 35)
        c.setFillColor(Color(39 / 255, 245 / 255, 242 / 255, alpha=0.35))  # pale blue, matches reference image
        c.drawCentredString(0, 0, wm_text)
        c.restoreState()
        c.save()

        overlay_buf.seek(0)
        overlay_page = PdfReader(overlay_buf).pages[0]

        for page in reader.pages:
            page.merge_page(overlay_page)
            writer.add_page(page)

        out_buf = io.BytesIO()
        writer.write(out_buf)
        return out_buf.getvalue(), pdf_type
    
    
    def _prepare_html(self, html, report_model=False):
            """Watermarking is now handled entirely in _render_qweb_pdf via PDF overlay.
            This override is intentionally a no-op passthrough — kept only so future
            devs know this hook was considered and deliberately not used for watermarks."""
            return super()._prepare_html(html, report_model=report_model)