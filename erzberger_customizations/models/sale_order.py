from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    job_reference = fields.Char(
        string="Job / Project Reference",
        help="Reference of the print job or project.",
    )

