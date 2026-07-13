from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    job_reference = fields.Char(
        string="Job / Project Reference",
        help="Reference of the print job or project."
    )

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_prepare_order_values(self, supplierinfo):
        values = super()._purchase_service_prepare_order_values(supplierinfo)

        values["job_reference"] = self.order_id.job_reference

        return values