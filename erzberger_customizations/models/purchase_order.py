from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    job_reference = fields.Char(
        string="Job / Project Reference",
        help="Reference of the print job or project.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.job_reference or not order.origin:
                continue
            sale_names = [n.strip() for n in order.origin.split(",")]
            sale_order = self.env["sale.order"].search(
                [("name", "in", sale_names)], limit=1
            )
            if sale_order and sale_order.job_reference:
                order.job_reference = sale_order.job_reference
        return orders