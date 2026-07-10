# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
from odoo.osv import expression
_logger = logging.getLogger(__name__)
import base64
from io import BytesIO
from openpyxl import load_workbook
BATCH_SIZE = 1000

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def cron_enable_track_inventory(self):
        domain = [
            ("type", "=", "consu"),
            ("is_storable", "=", False),
        ]

        total_updated = 0

        while True:
            products = self.search(domain, limit=BATCH_SIZE)

            if not products:
                break

            products.write({
                "is_storable": True,
            })

            total_updated += len(products)
            self.env.cr.commit()  # Optional for cron jobs with large datasets

            _logger.info(
                "Updated %s products in current batch. Total updated: %s",
                len(products),
                total_updated,
            )

        _logger.info(
            "Track Inventory enabled successfully for %s products.",
            total_updated,
        )

    @api.model
    def cron_enable_dropship_route(self):
        company_id = 2  # Erzberger Verpackung

        dropship_route = self.env.ref(
            "stock_dropshipping.route_drop_shipping",
            raise_if_not_found=False,
        )

        if not dropship_route:
            _logger.warning("Dropship route not found.")
            return

        products = self.search([
            ('company_id', '=', company_id),
            ('route_ids', 'not in', dropship_route.ids),
        ])

        _logger.info("Found %s products.", len(products))

        products.write({
            'route_ids': [(4, dropship_route.id)]
        })

        _logger.info("Dropship route enabled successfully.")

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

    def _cron_quotation_description_mapping(self):

        attachment = self.env['ir.attachment'].search([
            ('name', '=', 'quotation_description_mapping.xlsx')
        ], limit=1)

        if not attachment:
            _logger.info("Quotation description mapping file not found")
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
            quotation_description = row[1] and str(row[1]).strip()

            if not product_name:
                continue

            product = self.search([
                ('name', '=', product_name)
            ], limit=1)

            if product:
                product.description_sale = quotation_description or ""
                updated += 1
            else:
                not_found.append(product_name)

        _logger.info(
            "Quotation description mapping completed. Updated %s products",
            updated
        )

        for item in not_found:
            _logger.warning(
                "Product not found: %s",
                item
            )


    def _cron_set_company1_uom_to_piece(self):

        company = self.env['res.company'].browse(1)
        if not company.exists():
            _logger.info("Company 1 not found.")
            return

        uom_piece = self.env['uom.uom'].search([
            ('name', '=', 'Stück')
        ], limit=1)

        if not uom_piece:
            _logger.info("UoM 'Stück' not found.")
            return

        products = self.search([
            ('company_id', '=', company.id)
        ])

        _logger.info("Updating %s products...", len(products))

        products.write({
            'uom_id': uom_piece.id,
        })

        _logger.info("Finished updating Company 1 products.")

    def _cron_product_uom_weight_mapping(self):

        attachment = self.env['ir.attachment'].search([
            ('name', '=', 'uom_change_ver_cleaned.xlsx')
        ], limit=1)

        if not attachment:
            _logger.info("UoM mapping file not found")
            return

        workbook = load_workbook(
            filename=BytesIO(base64.b64decode(attachment.datas)),
            read_only=True
        )

        sheet = workbook.active

        updated = 0
        not_found = []
        uom_not_found = []

        for row in sheet.iter_rows(min_row=2, values_only=True):

            product_name = str(row[0]).strip() if row[0] else False
            uom_name = str(row[1]).strip() if row[1] else False
            weight = row[2]

            if not product_name:
                continue

            product = self.search([
                ('name', '=', product_name)
            ], limit=1)

            if not product:
                not_found.append(product_name)
                continue

            vals = {}

            # Update UoM
            if uom_name:
                uom = self.env['uom.uom'].search([
                    ('name', '=', uom_name)
                ], limit=1)

                if uom:
                    vals.update({
                        'uom_id': uom.id,
                    })
                else:
                    uom_not_found.append(
                        f"{product_name} -> {uom_name}"
                    )

            # Update Weight
            if weight not in (None, "", False):
                try:
                    vals['weight'] = float(weight)
                except Exception:
                    _logger.warning(
                        "Invalid weight '%s' for product '%s'",
                        weight,
                        product_name
                    )

            if vals:
                product.write(vals)
                updated += 1

        _logger.info(
            "UoM & Weight mapping completed. Updated %s products.",
            updated
        )

        for product_name in not_found:
            _logger.warning(
                "Product not found: %s",
                product_name
            )

        for item in uom_not_found:
            _logger.warning(
                "UoM not found: %s",
                item
            )

    def _cron_product_pos_category_mapping(self):

        attachment = self.env['ir.attachment'].search([
            ('name', '=', 'product_pos_category.xlsx')
        ], limit=1)

        if not attachment:
            _logger.info("POS Category mapping file not found.")
            return

        workbook = load_workbook(
            filename=BytesIO(base64.b64decode(attachment.datas)),
            read_only=True
        )

        sheet = workbook.active

        updated = 0
        product_not_found = []
        category_not_found = []

        for row in sheet.iter_rows(min_row=2, values_only=True):

            product_name = str(row[0]).strip() if row[0] else False
            category_name = str(row[1]).strip() if row[1] else False

            if not product_name:
                continue

            product = self.search([
                ('name', '=', product_name)
            ], limit=1)

            if not product:
                product_not_found.append(product_name)
                continue

            if not category_name:
                continue

            pos_category = self.env['pos.category'].search([
                ('name', '=', category_name)
            ], limit=1)

            if not pos_category:
                category_not_found.append(
                    f"{product_name} -> {category_name}"
                )
                continue

            product.write({
                'pos_categ_ids': [(6, 0, [pos_category.id])]
            })

            updated += 1

        _logger.info(
            "POS Category Mapping completed. Updated %s products.",
            updated
        )

        for product_name in product_not_found:
            _logger.warning(
                "Product not found: %s",
                product_name
            )

        for item in category_not_found:
            _logger.warning(
                "POS Category not found: %s",
                item
            )