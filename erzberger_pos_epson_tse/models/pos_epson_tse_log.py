# -*- coding: utf-8 -*-
from odoo import fields, models


class PosEpsonTseLog(models.Model):
    _name = 'pos.epson.tse.log'
    _description = 'Epson USB TSE Audit & Diagnostic Log'
    _order = 'create_date desc'

    config_id = fields.Many2one('pos.config', string="POS Config", ondelete='cascade')
    order_id = fields.Many2one('pos.order', string="POS Order", ondelete='set null')
    log_type = fields.Selection([
        ('start_tx', 'Start Transaction'),
        ('finish_tx', 'Finish Transaction'),
        ('status', 'Status Query'),
        ('error', 'Error / Offline'),
    ], string="Event Type", required=True, default='finish_tx')
    transaction_number = fields.Integer(string="TSE Transaction Number")
    signature_counter = fields.Integer(string="Signature Counter")
    message = fields.Text(string="Log Message")
    raw_request = fields.Text(string="Raw Request XML/JSON")
    raw_response = fields.Text(string="Raw Response XML/JSON")
