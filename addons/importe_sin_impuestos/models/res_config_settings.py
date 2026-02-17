from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    belero_tax_included = fields.Boolean(
        string="Mostrar importes con impuestos incluidos",
        help="Si se activa, los precios en vistas y reportes se mostrarán con el IVA incluido.",
        config_parameter='belero.tax_included' # Se guarda en ir.config_parameter
    )