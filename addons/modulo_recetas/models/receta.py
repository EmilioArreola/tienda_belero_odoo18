# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Receta(models.Model):
    _name = 'receta.receta'
    _description = 'Receta de Cocina'
    _order = 'name'

    # --- Información general ---
    name = fields.Char(
        string="Nombre de la Receta",
        required=True,
        translate=True
    )
    categoria_ids = fields.Many2many(
        'receta.categoria',
        string='Categorías',
        help="Categorías culinarias de la receta"
    )
    image_1920 = fields.Image(
        string="Imagen de la Receta",
        max_width=1920,
        max_height=1920
    )

    # --- Datos clave ---
    porciones = fields.Integer(
        string="Porciones",
        help="Cantidad de porciones que rinde la receta."
    )
    tiempo_preparacion = fields.Integer(
        string="Tiempo de preparación (min)",
        help="Tiempo total en minutos para preparar la receta."
    )
    dificultad = fields.Selection([
        ('facil', 'Fácil'),
        ('medio', 'Medio'),
        ('dificil', 'Difícil'),
    ], string='Dificultad', help="Nivel de dificultad de la receta.")

    # --- Contenido ---
    descripcion_corta = fields.Text(
        string="Descripción Corta",
        help="Breve resumen de la receta. Este campo es obligatorio.",
        translate=True,
        required=True
    )
    descripcion_larga = fields.Html(
        string="Descripción Detallada",
        help="Texto más extenso con historia o contexto de la receta.",
        sanitize=True,
        translate=True
    )
    
    # --- NUEVA LÓGICA DE INGREDIENTES ---
    ingrediente_ids = fields.Many2many(
        'receta.ingrediente',
        string="Ingredientes (Etiquetas)",
        help="Selecciona los ingredientes principales para enlazarlos a productos."
    )
    ingredientes_cantidades = fields.Html(
        string="Lista de Ingredientes y Cantidades",
        help="Escribe aquí la lista detallada para los visitantes, ej: 500 gr de Harina, 2 Huevos."
    )

    instrucciones = fields.Html(
        string="Modo de Preparación",
        help="Pasos detallados para preparar la receta.",
        sanitize=True,
        translate=True
    )

    # --- RESTRICCIÓN DE VALIDACIÓN ---
    @api.constrains('porciones', 'tiempo_preparacion')
    def _check_positive_values(self):
        for record in self:
            if record.porciones and record.porciones < 1:
                raise ValidationError("El número de porciones debe ser al menos 1.")
            if record.tiempo_preparacion and record.tiempo_preparacion < 1:
                raise ValidationError("El tiempo de preparación debe ser un número positivo.")

    # --- LÓGICA AUTOMÁTICA AL CREAR ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('descripcion_larga') and vals.get('descripcion_corta'):
                vals['descripcion_larga'] = vals['descripcion_corta']
        return super(Receta, self).create(vals_list)

    # --- LÓGICA AUTOMÁTICA AL EDITAR ---
    def write(self, vals):
        res = super(Receta, self).write(vals)
        for record in self.filtered(lambda r: not r.descripcion_larga):
            record.write({'descripcion_larga': record.descripcion_corta})
        return res