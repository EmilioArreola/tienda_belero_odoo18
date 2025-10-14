# -*- coding: utf-8 -*-
from odoo import models, fields

class Receta(models.Model):
    _name = 'receta.receta'
    _description = 'Modelo para almacenar recetas de cocina'

    # Campos principales
    name = fields.Char(string="Nombre de la Receta", required=True)
    descripcion_corta = fields.Text(string="Descripción Corta")
    
    # Contenido completo de la receta
    ingredientes = fields.Html(string="Ingredientes")
    instrucciones = fields.Html(string="Instrucciones")