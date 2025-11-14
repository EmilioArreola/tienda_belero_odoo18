from odoo import models, fields

class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    # Un solo campo que guarda el parámetro 'web.replace.url'
    url_replace_to = fields.Char(
        string='Palabra de Reemplazo (ej. smarts)',
        config_parameter='web.replace.url'
    )