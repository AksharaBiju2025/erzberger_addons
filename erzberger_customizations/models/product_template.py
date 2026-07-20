# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    hersteller = fields.Char(
        string="Hersteller",
    )

    referenz_hersteller = fields.Char(
        string="Referenz Hersteller",
    )