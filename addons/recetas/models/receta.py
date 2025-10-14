# models/receta.py
from odoo import models, fields, api

class Receta(models.Model):
    _name = 'recetas.receta'
    _description = 'Receta de Cocina'
    _order = 'create_date desc'
    _rec_name = 'name'  # para que se use correctamente el nombre


    name = fields.Char(string='Nombre de la Receta', required=True)
    descripcion_corta = fields.Char(string='Descripción Corta', size=100)
    imagen = fields.Image(string='Imagen', max_width=1024, max_height=1024)
    imagen_preview = fields.Image(string='Preview', related='imagen', max_width=256, max_height=256, store=True)
    
    # Información detallada
    tiempo_preparacion = fields.Integer(string='Tiempo de Preparación (min)')
    tiempo_coccion = fields.Integer(string='Tiempo de Cocción (min)')
    porciones = fields.Integer(string='Porciones', default=4)
    dificultad = fields.Selection([
        ('facil', 'Fácil'),
        ('medio', 'Medio'),
        ('dificil', 'Difícil')
    ], string='Dificultad', default='medio')
    
    # Contenido completo
    ingredientes = fields.Text(string='Ingredientes', required=True)
    preparacion = fields.Html(string='Preparación', required=True)
    notas = fields.Text(string='Notas Adicionales')
    
    # Categorización
    categoria_id = fields.Many2one('recetas.categoria', string='Categoría')
    tags_ids = fields.Many2many('recetas.tag', string='Etiquetas')
    
    active = fields.Boolean(string='Activo', default=True)
    
    @api.depends('tiempo_preparacion', 'tiempo_coccion')
    def _compute_tiempo_total(self):
        for record in self:
            record.tiempo_total = record.tiempo_preparacion + record.tiempo_coccion
    
    tiempo_total = fields.Integer(string='Tiempo Total', compute='_compute_tiempo_total', store=True)


class RecetaCategoria(models.Model):
    _name = 'recetas.categoria'
    _description = 'Categoría de Receta'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color')


class RecetaTag(models.Model):
    _name = 'recetas.tag'
    _description = 'Etiqueta de Receta'

    name = fields.Char(string='Nombre', required=True)
    color = fields.Integer(string='Color')