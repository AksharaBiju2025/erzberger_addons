# -*- coding: utf-8 -*-

from odoo import models, fields

import logging
from odoo.osv import expression
_logger = logging.getLogger(__name__)
import base64
from io import BytesIO
from openpyxl import load_workbook


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _cron_product_category_mapping_verpackungssysteme(self):

        attachment = self.env['ir.attachment'].search([
            ('name', '=', 'product_p_categ_maping _verpackungssysteme.xlsx')
        ], limit=1)

        if not attachment:
            _logger.info("Category mapping file not found")
            return

        workbook = load_workbook(
            filename=BytesIO(base64.b64decode(attachment.datas)),
            read_only=True
        )

        sheet = workbook.active

        updated = 0
        not_found = []

        for row in sheet.iter_rows(min_row=2, values_only=True):

            product_name = str(row[0]).strip() if len(row) > 0 and row[0] else False
            category_name = str(row[1]).strip() if len(row) > 1 and row[1] else False
            purchase_desc = str(row[2]).strip() if len(row) > 2 and row[2] else False

            if not product_name or not category_name:
                continue

            product = self.search([
                ('name', '=', product_name)
            ], limit=1)

            category = self.env['product.category'].search([
                ('name', '=', category_name)
            ], limit=1)
            if product:
                product.description_purchase = purchase_desc

            if product and category:
                product.categ_id = category.id
                updated += 1
            else:
                not_found.append(
                    "%s -> %s" % (
                        product_name,
                        category_name
                    )
                )

        _logger.info(
            "Category mapping completed. Updated %s products",
            updated
        )

        for item in not_found:
            _logger.warning(item)


    def _cron_product_category_mapping_holzkunst(self):

        attachment = self.env['ir.attachment'].search([
            ('name', '=', 'product_p_categ_maping _holzkunst.xlsx')
        ], limit=1)

        if not attachment:
            _logger.info("Category mapping file not found")
            return

        workbook = load_workbook(
            filename=BytesIO(base64.b64decode(attachment.datas)),
            read_only=True
        )

        sheet = workbook.active

        updated = 0
        not_found = []

        for row in sheet.iter_rows(min_row=2, values_only=True):

            product_name = row[0] and str(row[0]).strip()
            category_name = row[1] and str(row[1]).strip()

            if not product_name or not category_name:
                continue

            product = self.search([
                ('name', '=', product_name)
            ], limit=1)

            category = self.env['product.category'].search([
                ('name', '=', category_name)
            ], limit=1)

            if product and category:
                product.categ_id = category.id
                updated += 1
            else:
                not_found.append(
                    "%s -> %s" % (
                        product_name,
                        category_name
                    )
                )

        _logger.info(
            "Category mapping completed. Updated %s products",
            updated
        )

        for item in not_found:
            _logger.warning(item)
