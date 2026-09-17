# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    po_number = fields.Char(
        string="PO Number",
        compute="_compute_po_number",
        help="Linked Purchase Order Numbers"
    )

    @api.depends('invoice_line_ids', 'invoice_origin')
    def _compute_po_number(self):
        for move in self:
            sale_lines = move.invoice_line_ids.mapped(lambda l: getattr(l, 'sale_line_ids', self.env['sale.order.line']))
            sale_orders = sale_lines.mapped('order_id')
            if not sale_orders and move.invoice_origin:
                sale_orders = self.env['sale.order'].search([('name', '=', move.invoice_origin)])
            
            po_lines = sale_orders.mapped('order_line').mapped(lambda l: getattr(l, 'purchase_line_ids', self.env['purchase.order.line']))
            pos = po_lines.mapped('order_id')
            if not pos and sale_orders:
                pos = self.env['purchase.order'].search([('origin', 'in', sale_orders.mapped('name'))])
                groups = sale_orders.mapped('procurement_group_id')
                if not pos and groups:
                    pos = self.env['purchase.order'].search([('group_id', 'in', groups.ids)])
            
            if not pos and getattr(move, 'purchase_id', False):
                pos = move.purchase_id

            move.po_number = ", ".join(pos.mapped('name')) if pos else False

    # def action_print_pdf(self):
    #     self.ensure_one()

    #     if (
    #         self.company_id.use_custom_sale_report
    #         and self.move_type in ("out_invoice", "out_refund")
    #     ):
    #         return self.env.ref(
    #             "erzberger_sale_report.action_report_invoice_custom"
    #         ).report_action(self)

    #     return super().action_print_pdf()
    
    
    def action_print_pdf(self):
        self.ensure_one()

        if (
            self.company_id.use_custom_sale_report
            and self.move_type in ("out_invoice", "out_refund")
        ):
            return self.env.ref(
                "erzberger_sale_report.action_report_invoice_custom"
            ).report_action(self)

        else:
            return self.env.ref(
                "erzberger_sale_report.action_report_invoice_holzenberg"
            ).report_action(self)

    def preview_invoice(self):
        self.ensure_one()

        if (
            self.company_id.use_custom_sale_report
            and self.move_type in ("out_invoice", "out_refund")
        ):
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': self.get_portal_url(),
            }

        return super().preview_invoice()