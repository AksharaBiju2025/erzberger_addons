# models/res_company.py

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    report_company_description1 = fields.Html(
        string="Report Company Description1",
        sanitize=False,
    )
    report_company_description2 = fields.Html(
        string="Report Company Description2",
        sanitize=False,
    )
    use_custom_sale_report = fields.Boolean(
        string="Use Custom Sale Order Report"
    )