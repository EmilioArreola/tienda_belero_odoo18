from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    belero_tax_included = fields.Boolean(
        string="Mostrar importes con impuestos incluidos",
        help="Si se activa, los precios en vistas y reportes se mostrarán con el IVA incluido.",
        config_parameter='belero.tax_included'
    )

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Este es el campo que Odoo no encontraba
    belero_tax_mode = fields.Selection([
        ('on', 'on'),
        ('off', 'off')
    ], string="Modo de Impuestos Portal", default='on')