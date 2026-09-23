# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_l10n_de_epson_tse_enabled = fields.Boolean(
        related='pos_config_id.l10n_de_epson_tse_enabled',
        readonly=False
    )
    pos_l10n_de_epson_tse_ip = fields.Char(
        related='pos_config_id.l10n_de_epson_tse_ip',
        readonly=False
    )
    pos_l10n_de_epson_tse_port = fields.Integer(
        related='pos_config_id.l10n_de_epson_tse_port',
        readonly=False
    )
    pos_l10n_de_epson_tse_protocol = fields.Selection(
        related='pos_config_id.l10n_de_epson_tse_protocol',
        readonly=False
    )
    pos_l10n_de_epson_tse_devid = fields.Char(
        related='pos_config_id.l10n_de_epson_tse_devid',
        readonly=False
    )
    pos_l10n_de_epson_tse_client_id = fields.Char(
        related='pos_config_id.l10n_de_epson_tse_client_id',
        readonly=False
    )
    pos_l10n_de_epson_tse_serial = fields.Char(
        related='pos_config_id.l10n_de_epson_tse_serial',
        readonly=False
    )
    pos_l10n_de_epson_tse_test_mode = fields.Boolean(
        related='pos_config_id.l10n_de_epson_tse_test_mode',
        readonly=False
    )
