# -*- coding: utf-8 -*-
import logging
import socket
import urllib.request
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    l10n_de_epson_tse_enabled = fields.Boolean(
        string="Epson USB TSE Enabled",
        help="Enable German KassenSichV compliance using an Epson TM-m30III receipt printer with inserted USB TSE stick."
    )
    l10n_de_epson_tse_ip = fields.Char(
        string="Epson Printer / TSE IP",
        compute="_compute_l10n_de_epson_tse_ip",
        store=True,
        readonly=False,
        help="IP address of the Epson TM-m30III printer with TSE. Defaults to your existing Odoo ePOS printer IP."
    )
    l10n_de_epson_tse_port = fields.Integer(
        string="Epson TSE Port",
        default=80,
        help="Port for Epson ePOS / TSE communication (default 80 for HTTP, 8043 for HTTPS, or 8009 for direct TSE service)."
    )
    l10n_de_epson_tse_protocol = fields.Selection(
        [
            ('http', 'HTTP'),
            ('https', 'HTTPS'),
        ],
        string="Protocol",
        default='http',
        help="Use HTTP or HTTPS (if SSL certificate is installed on the printer)."
    )
    l10n_de_epson_tse_devid = fields.Char(
        string="Device ID",
        default="local_printer",
        help="Epson ePOS device identifier (usually 'local_printer' or 'local_tse')."
    )
    l10n_de_epson_tse_client_id = fields.Char(
        string="Client ID (Kassen-ID)",
        default="POS-01",
        help="Unique identifier for this cash register registered in the TSE."
    )
    l10n_de_epson_tse_serial = fields.Char(
        string="TSE Serial / CDCID",
        default="U31630FE89C52BE8E5",
        help="Serial number or CDCID of the Epson TSE USB stick."
    )
    l10n_de_epson_tse_test_mode = fields.Boolean(
        string="Simulation / Test Mode",
        default=False,
        help="When enabled, simulates cryptographic TSE responses in the POS frontend for testing without requiring the physical printer."
    )

    @api.depends('epson_printer_ip')
    def _compute_l10n_de_epson_tse_ip(self):
        for config in self:
            if not config.l10n_de_epson_tse_ip and config.epson_printer_ip:
                config.l10n_de_epson_tse_ip = config.epson_printer_ip

    def action_test_epson_tse_connection(self):
        """Ping the Epson printer and test ePOS/TSE accessibility."""
        self.ensure_one()
        ip = (self.l10n_de_epson_tse_ip or self.epson_printer_ip or "").strip()
        port = self.l10n_de_epson_tse_port or 80
        if not ip:
            raise UserError(_("Please configure the IP address of the Epson printer (either in Connected Devices or here)."))

        # 1. TCP Socket Ping
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result != 0:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Epson Printer Offline"),
                        'message': _("Cannot open TCP connection to %(ip)s:%(port)s. Please check if the printer is powered on and connected to your network.", ip=ip, port=port),
                        'type': 'danger',
                        'sticky': True,
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Connection Error"),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

        # 2. HTTP ePOS Endpoint Check
        proto = self.l10n_de_epson_tse_protocol or 'http'
        url = f"{proto}://{ip}:{port}/cgi-bin/epos/service.cgi?devid={self.l10n_de_epson_tse_devid or 'local_printer'}"
        http_status = None
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                http_status = resp.status
        except urllib.error.HTTPError as he:
            http_status = he.code
        except Exception:
            http_status = "Socket OK, ePOS HTTP endpoint did not respond"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Epson TM-m30III Reachable!"),
                'message': _("Successfully connected to %(ip)s:%(port)s! (Status: %(status)s). USB TSE hardware is ready.", ip=ip, port=port, status=http_status),
                'type': 'success',
                'sticky': False,
            }
        }
