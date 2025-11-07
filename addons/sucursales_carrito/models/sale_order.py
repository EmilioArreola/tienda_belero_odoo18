# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Creamos un campo de tipo 'Selección' que coincide
    # con los valores (values) de tu archivo templates.xml
    sucursal_recogida = fields.Selection([
        ('escuadron_201', 'Escuadrón 201 #300, Antiguo Aereopuerto'),
        ('lazaro_cardenas', 'Av Lázaro Cárdenas 503-3, Col. Guelatao, Santa Lucía'),
        ('cosijoeza', 'Calle Cosijoeza #216-A, Barrio de Jalatlaco'),
        ('eucaliptos', 'Eucaliptos #215 В, Col. Reforma, 68050'),
        ('riveras', 'Libramiento Riveras del Atoyac #122-2'),
        ('diaz_ordaz', 'Díaz Ordaz #710, Col. Centro'),
        ('eduardo_mata', 'Av. Eduardo Mata #2302, Periférico'),
        ('cristobal_colon', 'Carretera Cristóbal Colón #202, Santa Rosa'),
        ('yagul', 'Calle Yagul esq. Cosijopi #122-A'),
        ('vicente_guerrero', 'Vicente Guerrero, Centro, Oaxaca'),
    ], string='Sucursal de Recogida', 
       copy=False) # copy=False evita que se copie al duplicar una cotización