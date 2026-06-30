from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    job_reference = fields.Char(
        string="Job / Project Reference",
        help="Reference of the print job or project."
    )