# models/ingrediente_linea.py
from odoo import models, fields

class RecetaIngredienteLinea(models.Model):
    _name = 'receta.ingrediente.linea'
    _description = 'Línea de Ingrediente para Receta'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    receta_id = fields.Many2one('receta.receta', string='Receta', required=True, ondelete='cascade')

    # Relación con nuestro catálogo maestro de ingredientes
    ingrediente_id = fields.Many2one('receta.ingrediente', string='Ingrediente', required=True)

    # Cantidad y Unidad de Medida
    cantidad = fields.Float(string='Cantidad', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida')