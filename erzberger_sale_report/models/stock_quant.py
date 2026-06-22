# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

from odoo import models, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def cron_set_company_stock_zero(self):
        company_id = 2

        quants = self.search([
            ('company_id', '=', company_id),
            ('location_id.usage', '=', 'internal'),
            ('quantity', '!=', 0),
        ])

        _logger.info("Found %s quants", len(quants))

        for quant in quants:
            quant.inventory_quantity = 0

        quants.action_apply_inventory()

        _logger.info("Inventory adjustment applied")