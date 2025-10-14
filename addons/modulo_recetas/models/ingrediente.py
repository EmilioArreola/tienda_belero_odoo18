# models/ingrediente.py
from odoo import models, fields

class RecetaIngrediente(models.Model):
    _name = 'receta.ingrediente'
    _description = 'Etiqueta de Ingrediente para Recetas'
    _order = 'name'

    name = fields.Char(string="Nombre del Ingrediente", required=True)
    
    # --- CAMPO AÑADIDO ---
    # Enlace opcional a un producto de tu tienda
    product_id = fields.Many2one(
        'product.product', 
        string='Producto Vendible',
        help="Si este ingrediente corresponde a un producto de tu tienda, selecciónalo aquí."
    )