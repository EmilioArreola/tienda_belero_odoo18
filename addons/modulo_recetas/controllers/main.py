# -*- coding: utf-8 -*-
import unicodedata
from odoo import http
from odoo.http import request

def quitar_acentos(texto):
    if not texto:
        return ''
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return "".join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn').lower()


class RecetasWebsite(http.Controller):

    RECETAS_PER_PAGE = 12

    @http.route(['/recetas', '/recetas/page/<int:page>'], type='http', auth="public", website=True)
    def mostrar_recetas(self, page=1, **kw):
        search_term = kw.get('search', '').strip()
        todas_las_recetas = request.env['receta.receta'].search([])

        if search_term:
            search_terms = [quitar_acentos(t) for t in search_term.split()]
            recetas_filtradas = []

            for receta in todas_las_recetas:
                # Texto normalizado de receta, categorías e ingredientes
                nombre_normalizado = quitar_acentos(receta.name)
                categorias_normalizadas = [quitar_acentos(c.name) for c in receta.categoria_ids]
                ingredientes_normalizados = [quitar_acentos(i.name) for i in receta.ingrediente_ids]

                # Verificamos si todos los términos de búsqueda están presentes en alguno de los campos
                match = all(
                    any(
                        term in nombre_normalizado or
                        any(term in cat for cat in categorias_normalizadas) or
                        any(term in ing for ing in ingredientes_normalizados)
                        for term in [t]
                    ) for t in search_terms
                )

                if match:
                    recetas_filtradas.append(receta)

            recetas_finales = recetas_filtradas
        else:
            recetas_finales = todas_las_recetas

        total_recetas = len(recetas_finales)

        pager = request.website.pager(
            url='/recetas',
            total=total_recetas,
            page=page,
            step=self.RECETAS_PER_PAGE,
            url_args={'search': search_term} if search_term else {}
        )

        offset = pager['offset']
        recetas_de_la_pagina = recetas_finales[offset: offset + self.RECETAS_PER_PAGE]

        return request.render('modulo_recetas.pagina_recetas_lista', {
            'recetas': recetas_de_la_pagina,
            'search': search_term,
            'pager': pager,
        })

    @http.route('/recetas/<model("receta.receta"):receta>', type='http', auth="public", website=True)
    def mostrar_detalle_receta(self, receta, **kw):
        return request.render('modulo_recetas.pagina_receta_detalle', {
            'receta': receta
        })
