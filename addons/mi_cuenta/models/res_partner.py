# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Creamos un campo nuevo para guardar lo que escriban en "Régimen"
    # Le pongo 'x_' para indicar que es personalizado, aunque no es obligatorio.
    x_regimen_fiscal = fields.Char(string='Régimen Fiscal')