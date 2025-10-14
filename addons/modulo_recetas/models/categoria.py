# models/categoria.py
from odoo import models, fields

class RecetaCategoria(models.Model):
    _name = 'receta.categoria'
    _description = 'Categoría para recetas de cocina'

    name = fields.Char(string="Nombre de la Categoría", required=True)
    color = fields.Integer(string='Color') # <-- ¡LÍNEA NUEVA!