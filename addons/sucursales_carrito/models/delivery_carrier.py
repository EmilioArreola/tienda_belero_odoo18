# En un archivo nuevo: models/delivery_carrier.py
from odoo import models, fields

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    es_recogida_tienda = fields.Boolean(
        string='Es Recogida en Tienda',
        help='Marque esta opción si este método de entrega requiere que el cliente recoja en una sucursal'
    )