# -*- coding: utf-8 -*-
import unicodedata
from odoo import http
from odoo.http import request

# --- Función Auxiliar para quitar acentos y convertir a minúsculas ---
def quitar_acentos(texto):
    if not texto:
        return ''
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return "".join(
        c for c in texto_normalizado if unicodedata.category(c) != 'Mn'
    ).lower()


class RecetasWebsite(http.Controller):

    @http.route('/recetas', type='http', auth="public", website=True)
    def mostrar_recetas(self, **kw):
        search_term = kw.get('search')
        
        todas_las_recetas = request.env['receta.receta'].search([])
        
        if search_term:
            search_term_normalizado = quitar_acentos(search_term)
            recetas_filtradas = []
            
            for receta in todas_las_recetas:
                nombre_normalizado = quitar_acentos(receta.name)
                
                # --- LÓGICA ACTUALIZADA PARA BUSCAR EN MÚLTIPLES CATEGORÍAS ---
                categoria_coincide = False
                # Iteramos sobre todas las categorías de la receta
                for categoria in receta.categoria_ids:
                    categoria_normalizada = quitar_acentos(categoria.name)
                    if search_term_normalizado in categoria_normalizada:
                        categoria_coincide = True
                        break # Si encontramos una, no es necesario seguir
                
                # Comparamos con el nombre O si hubo coincidencia en alguna categoría
                if search_term_normalizado in nombre_normalizado or categoria_coincide:
                    recetas_filtradas.append(receta)
            
            recetas = recetas_filtradas
        else:
            recetas = todas_las_recetas
        
        return request.render('modulo_recetas.pagina_recetas_lista', {
            'recetas': recetas,
            'search': search_term, 
        })
    
    # --- PÁGINA DE DETALLE DE UNA RECETA ---
    @http.route('/recetas/<model("receta.receta"):receta>', type='http', auth="public", website=True)
    def mostrar_detalle_receta(self, receta, **kw):
        return request.render('modulo_recetas.pagina_receta_detalle', {
            'receta': receta
        })