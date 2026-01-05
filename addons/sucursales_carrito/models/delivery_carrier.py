from odoo import models, fields

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    es_recogida_tienda = fields.Boolean(
        string='Es Recogida en Tienda',
        help='Si está activo, el cliente deberá seleccionar una sucursal'
    )
