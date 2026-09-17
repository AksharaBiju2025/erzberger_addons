# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    po_number = fields.Char(
        string="PO Number",
        compute="_compute_po_number",
        help="Linked Purchase Order Numbers"
    )

    @api.depends('origin', 'move_ids')
    def _compute_po_number(self):
        for picking in self:
            pos = self.env['purchase.order']

            # Direct purchase order relation, if available
            if getattr(picking, 'purchase_id', False):
                pos |= picking.purchase_id

            # Get Sale Order from Delivery
            sale_orders = self.env['sale.order']

            if getattr(picking, 'sale_id', False):
                sale_orders |= picking.sale_id

            # Get Sale Order through stock moves
            if not sale_orders and picking.move_ids:
                sale_lines = picking.move_ids.mapped('sale_line_id')
                sale_orders |= sale_lines.mapped('order_id')

            # Fallback: use origin
            if not sale_orders and picking.origin:
                sale_orders |= self.env['sale.order'].search([
                    ('name', '=', picking.origin)
                ])

            # Get Purchase Orders through Sale Order Lines
            if sale_orders:
                po_lines = sale_orders.mapped('order_line').mapped(
                    'purchase_line_ids'
                )
                pos |= po_lines.mapped('order_id')

                # Fallback: PO origin
                if not pos:
                    pos |= self.env['purchase.order'].search([
                        ('origin', 'in', sale_orders.mapped('name'))
                    ])

            # Final fallback: procurement group on picking
            if not pos and getattr(picking, 'group_id', False):
                pos |= self.env['purchase.order'].search([
                    ('group_id', '=', picking.group_id.id)
                ])

            picking.po_number = ', '.join(pos.mapped('name')) if pos else False

    def action_print_delivery_custom(self):
        self.ensure_one()

        if self.company_id.use_custom_sale_report:
            return self.env.ref(
                "erzberger_sale_report.action_report_delivery_note"
            ).report_action(self)

        return self.env.ref(
            "erzberger_sale_report.action_report_delivery_note_holzenberg"
        ).report_action(self)