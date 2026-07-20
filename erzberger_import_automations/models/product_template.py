# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)
import base64
import io
from io import BytesIO
from openpyxl import load_workbook
BATCH_SIZE = 1000

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def normalize(text):
        return " ".join(str(text).split())
    # ------------------------------------------------------------------
    # This function about missing product categories will update while trigger this function
    # ------------------------------------------------------------------
    @api.model
    def map_product_categories_from_excel(self):
        """
        1. Fetch all product.template records where categ_id is False.
        2. For each, take its Name and look it up in the Excel's "Name"
           column (col B).
        3. If found, read that row's "Kategorie des Kassensystems" value
           (col G).
        4. Search for an EXISTING product.category with that exact name
           (no creation).
        5. If found, write categ_id on the product.
        """
        attachment = self.env["ir.attachment"].search(
            [("name", "=", '500_products_holz.xlsx')], limit=1
        )
        if not attachment:
            print(f"Attachment '{'500_products_holz.xlsx'}' not found — aborting.")
            return False

        import openpyxl  # local import keeps module load light if unused

        file_bytes = base64.b64decode(attachment.datas)
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        ws = wb.active

        # Map header name -> column index (1-based), read from row 1
        headers = {}
        for idx, cell in enumerate(ws[1]):
            if cell.value is not None:
                headers[str(cell.value).strip()] = idx + 1
        name_col = headers.get("Name")
        cat_col = headers.get("Produktkategorie")

        if not name_col or not cat_col:
            print(
                f"Required columns not found. Name col: {name_col}, "
                f"Kategorie des Kassensystems col: {cat_col}"
            )
            return False

        # Build: { product name (stripped) : category text from col G }
        by_name = {}
        for row in ws.iter_rows(min_row=2, values_only=False):
            name_val = row[name_col - 1].value
            cat_val = row[cat_col - 1].value
            if not name_val or not cat_val:
                continue
            by_name[str(name_val).strip()] = str(cat_val).strip()

        # Step 1: fetch products with no category set
        products = self.search([("categ_id", "=", False)])
        print(f"Found {len(products)} products with categ_id = False")

        Category = self.env["product.category"]
        category_cache = {}   # category text -> product.category record / None
        matched = 0
        no_excel_row = []      # product name not found in Excel at all
        no_category_match = [] # Excel had a value, but no matching product.category

        for product in products:
            product_name = (product.name or "").strip()
            cat_text = by_name.get(product_name)

            if not cat_text:
                no_excel_row.append(product.id)
                continue

            if cat_text not in category_cache:
                category_cache[cat_text] = Category.search(
                    [("name", "=", cat_text)], limit=1
                ) or None
            category = category_cache[cat_text]

            if not category:
                no_category_match.append((product.id, cat_text))
                continue

            product.write({"categ_id": category.id})
            matched += 1

        print(
            f"Category mapping done. Matched: {matched} | "
            f"No Excel row: {len(no_excel_row)} | "
            f"Category not found in system: {len(no_category_match)}"
        )
        if no_excel_row:
            print(f"Products with no matching Excel row: {no_excel_row}")
        if no_category_match:
            print(
                "Products where category text had no existing "
                f"product.category: {no_category_match}"
            )

        return True


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

    def _cron_product_vendor_mapping(self):

        attachment = self.env["ir.attachment"].search([
            ("name", "=", "product_vendor_mapping.xlsx")
        ], limit=1)

        if not attachment:
            _logger.info("Product vendor mapping file not found.")
            return

        workbook = load_workbook(
            filename=BytesIO(base64.b64decode(attachment.datas)),
            read_only=True,
            data_only=True,
        )

        sheet = workbook.active

        updated = 0
        product_not_found = []
        vendor_not_found = []

        SupplierInfo = self.env["product.supplierinfo"]
        Partner = self.env["res.partner"]

        for row in sheet.iter_rows(
                min_row=2,
                min_col=1,
                max_col=2,
                values_only=True,
        ):
            product_name = str(row[0]).strip() if row[0] else False
            vendor_name = str(row[1]).strip() if len(row) > 1 and row[1] else False

            if not product_name or not vendor_name:
                continue

            product = self.search([
                ("name", "=", product_name)
            ], limit=1)

            if not product:
                product_not_found.append(product_name)
                continue

            vendor = Partner.search([
                ("name", "=", vendor_name)
            ], limit=1)

            if not vendor:
                vendor_not_found.append(
                    f"{product_name} -> {vendor_name}"
                )
                continue

            existing_supplier = SupplierInfo.search([
                ("product_tmpl_id", "=", product.id),
                ("partner_id", "=", vendor.id),
            ], limit=1)

            if existing_supplier:
                continue

            SupplierInfo.create({
                "product_tmpl_id": product.id,
                "partner_id": vendor.id,
                "min_qty": 0,
            })

            updated += 1

        _logger.info(
            "Product Vendor Mapping completed. Updated %s products.",
            updated,
        )

        for product_name in product_not_found:
            _logger.warning("Product not found: %s", product_name)

        for item in vendor_not_found:
            _logger.warning("Vendor not found: %s", item)

    def _cron_update_supplierinfo_company(self):
        SupplierInfo = self.env["product.supplierinfo"].sudo()

        supplier_infos = SupplierInfo.search([
            ("company_id", "=", 1),
        ])

        count = len(supplier_infos)

        supplier_infos.write({
            "company_id": 2,
        })

        _logger.info(
            "SupplierInfo Company Update completed. "
            "Updated %s supplier records from company 1 to company 2.",
            count,
        )