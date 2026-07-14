from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    job_reference = fields.Char(
        string=_("Auftrags- / Projektreferenz"),
        help=_("Referenz des Druckauftrags oder Projekts."),
    )

