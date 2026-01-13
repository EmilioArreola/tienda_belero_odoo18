# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

print("\n\n" + "="*50)
print("¡¡¡HOLA!!! EL ARCHIVO RES_PARTNER.PY SE ESTÁ CARGANDO")
print("="*50 + "\n\n")

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_regimen_fiscal = fields.Char(string="Régimen Fiscal (MX)")
    x_uso_cfdi = fields.Char(string="Uso de CFDI (MX)")