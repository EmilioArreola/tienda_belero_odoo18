# -*- coding: utf-8 -*-
import base64
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Spacer, Preformatted
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from odoo import http
from odoo.http import request, content_disposition
import os

_logger = logging.getLogger(__name__)

# Fuente UTF-8 para acentos - Registrar con manejo de errores
try:
    pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    
    # Intentar registrar fuentes adicionales
    font_paths = {
        'DejaVu-Bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        'DejaVu-Italic': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',
        'DejaVu-BoldItalic': '/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'
    }
    
    for font_name, font_path in font_paths.items():
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            _logger.info(f"Fuente {font_name} registrada correctamente")
        else:
            _logger.warning(f"No se encontró la fuente en {font_path}")
    
    # Solo registrar familia si todas las fuentes existen
    if all(os.path.exists(path) for path in font_paths.values()):
        pdfmetrics.registerFontFamily('DejaVu',
                                      normal='DejaVu',
                                      bold='DejaVu-Bold',
                                      italic='DejaVu-Italic',
                                      boldItalic='DejaVu-BoldItalic')
        _logger.info("Familia de fuentes DejaVu registrada correctamente")
    else:
        _logger.warning("No se pudo registrar la familia de fuentes completa")
        
except Exception as e:
    _logger.error(f"Error al registrar fuentes: {e}")

class RecetasWebsite(http.Controller):

    RECETAS_PER_PAGE = 12

    # --- LISTA DE RECETAS ---
    @http.route(['/recetas', '/recetas/page/<int:page>'], type='http', auth="public", website=True)
    def mostrar_recetas(self, page=1, **kw):
        search_term = kw.get('search', '').strip()
        todas_las_recetas = request.env['receta.receta'].search([])

        if search_term:
            search_terms = [t.lower() for t in search_term.split()]
            recetas_filtradas = []
            for receta in todas_las_recetas:
                nombre = receta.name.lower()
                categorias = [c.name.lower() for c in receta.categoria_ids]
                ingredientes = [i.name.lower() for i in receta.ingrediente_ids]
                match = all(
                    any(term in nombre or any(term in c for c in categorias) or any(term in i for i in ingredientes) 
                        for term in [t])
                    for t in search_terms
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

    # --- DETALLE DE RECETA ---
    @http.route('/recetas/<model("receta.receta"):receta>', type='http', auth="public", website=True)
    def mostrar_detalle_receta(self, receta, **kw):
        return request.render('modulo_recetas.pagina_receta_detalle', {
            'receta': receta
        })

    # --- DESCARGAR RECETA EN PDF ---
    @http.route('/recetas/<model("receta.receta"):receta>/pdf', type='http', auth="public", website=True)
    def descargar_receta_pdf(self, receta, **kw):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        estilos = getSampleStyleSheet()
        estilo_normal = ParagraphStyle('normal', parent=estilos['Normal'], fontName='DejaVu', fontSize=10, leading=14)
        estilo_heading2 = ParagraphStyle('heading2', parent=estilos['Heading2'], fontName='DejaVu', fontSize=12, leading=16)
        elementos = []

        # Título
        estilo_heading2_centrado = ParagraphStyle(
            'heading2_centrado',
            parent=estilo_heading2,
            fontSize=24,  # Tamaño de la fuente en puntos
            alignment=1  # 0=izquierda, 1=centro, 2=derecha, 4=justificado
        )

        elementos.append(Paragraph(f"<b>{receta.name}</b>", estilo_heading2_centrado))
        elementos.append(Spacer(1, 0.25*inch))
        elementos.append(HRFlowable(width="100%", thickness=1, color='lightgrey'))
        elementos.append(Spacer(1, 0.2*inch))

        # Imagen
        if receta.image_1920:
            try:
                imagen_bytes = base64.b64decode(receta.image_1920)
                imagen_buffer = BytesIO(imagen_bytes)
                img = Image(imagen_buffer, width=4*inch, height=3*inch)
                elementos.append(img)
                elementos.append(Spacer(1, 0.2*inch))
            except Exception as e:
                _logger.warning(f"No se pudo cargar la imagen de la receta {receta.id}: {e}")

        # Información básica
        info_data = []
        info_values = []

        if receta.porciones:
            info_values.append(f"Porciones: {receta.porciones}")
        if receta.tiempo_preparacion:
            info_values.append(f"Tiempo de preparación: {receta.tiempo_preparacion} minutos")
        if receta.dificultad:
            dificultad_map = {'facil':'Fácil','medio':'Medio','dificil':'Difícil'}
            dif = receta.dificultad.lower()
            dif = dificultad_map.get(dif, receta.dificultad.capitalize())
            info_values.append(f"Dificultad: {dif}")

        if info_values:
            # Crear una tabla con las columnas necesarias
            info_data = [info_values]
            
            # Calcular el ancho de cada columna (distribuir equitativamente)
            num_cols = len(info_values)
            col_width = 6.5*inch / num_cols  # Ancho total de página menos márgenes
            
            info_table = Table(info_data, colWidths=[col_width] * num_cols)
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elementos.append(info_table)
            elementos.append(Spacer(1, 0.25*inch))
            elementos.append(HRFlowable(width="100%", thickness=0.5, color='lightgrey'))
            elementos.append(Spacer(1, 0.2*inch))

        # --- Ingredientes ---
        if receta.ingredientes_cantidades:
            elementos.append(Paragraph("<b>Ingredientes:</b>", estilo_heading2))
            elementos.append(Spacer(1, 0.1*inch))
            
            import re
            from html import unescape
            
            # Limpiar HTML
            texto_limpio = receta.ingredientes_cantidades
            texto_limpio = re.sub(r'<[^>]+>', '', texto_limpio)
            texto_limpio = unescape(texto_limpio)
            
            # Dividir por saltos de línea
            lineas = [l.strip() for l in texto_limpio.splitlines() if l.strip()]
            
            ingredientes_completos = []
            i = 0
            
            while i < len(lineas):
                linea_actual = lineas[i]
                
                # Detectar si es cantidad (número, fracción, o palabra de cantidad seguida de descripción incompleta)
                # Números enteros, decimales, fracciones unicode (½, ¼, etc.)
                es_cantidad = re.match(r'^[\d½¼¾⅓⅔⅛⅜⅝⅞]+\.?\d*$', linea_actual)
                
                # Detectar palabras de cantidad/medida solas (Cubos, Rebanadas, Pizca, etc.)
                palabras_cantidad = ['cubos', 'rebanadas', 'pizca', 'pizcas', 'taza', 'tazas', 
                                    'cucharada', 'cucharadas', 'cucharadita', 'cucharaditas',
                                    'gramos', 'gram', 'ml', 'litros', 'kg', 'aceite']
                es_palabra_cantidad = linea_actual.lower() in palabras_cantidad
                
                if (es_cantidad or es_palabra_cantidad) and i + 1 < len(lineas):
                    # Unir con la siguiente línea
                    ingrediente_completo = linea_actual + ' ' + lineas[i + 1]
                    ingredientes_completos.append(ingrediente_completo)
                    i += 2  # Saltar ambas líneas
                else:
                    # Es un ingrediente completo
                    ingredientes_completos.append(linea_actual)
                    i += 1
            
            # Numerarlos
            for idx, ingrediente in enumerate(ingredientes_completos, 1):
                ingrediente_escapado = ingrediente.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                texto = f"• {ingrediente_escapado}"
                elementos.append(Paragraph(texto, estilo_normal))
            
            elementos.append(Spacer(1, 0.12*inch))

        # --- Modo de preparación ---
        if receta.instrucciones:
            elementos.append(Paragraph("<b>Modo de preparación:</b>", estilo_heading2))
            elementos.append(Spacer(1, 0.1*inch))
            
            import re
            from html import unescape
            
            # Limpiar HTML
            texto_limpio = receta.instrucciones
            texto_limpio = re.sub(r'<[^>]+>', '', texto_limpio)
            texto_limpio = unescape(texto_limpio)
            
            # Remover numeración existente de cada línea
            lineas = texto_limpio.splitlines()
            lineas_sin_numero = []
            for linea in lineas:
                linea_limpia = re.sub(r'^\d+[\.\-\)]+\s*', '', linea.strip())
                if linea_limpia:
                    lineas_sin_numero.append(linea_limpia)
            
            # Unir todo en un solo texto
            texto_unido = ' '.join(lineas_sin_numero)
            
            # Dividir por puntos seguidos de mayúscula (fin de instrucción)
            instrucciones = re.split(r'\.\s+(?=[A-Z])', texto_unido)
            
            # Numerarlas
            for idx, instruccion in enumerate(instrucciones, 1):
                instruccion = instruccion.strip()
                if instruccion:
                    # Agregar punto final si no lo tiene
                    if not instruccion.endswith('.'):
                        instruccion += '.'
                    instruccion_escapada = instruccion.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    texto = f"{idx}. {instruccion_escapada}"
                    elementos.append(Paragraph(texto, estilo_normal))
            
            elementos.append(Spacer(1, 0.2*inch))

        # Descripción detallada
        if receta.descripcion_larga:
            elementos.append(Paragraph("<b>Descripción detallada:</b>", estilo_heading2))
            elementos.append(Spacer(1, 0.1*inch))
            
            # Limpiar HTML pero mantener negritas y cursivas
            import re
            from html import unescape
            texto_limpio = receta.descripcion_larga
            
            # Convertir etiquetas de negrita HTML a formato ReportLab
            texto_limpio = re.sub(r'<strong>', '<b>', texto_limpio, flags=re.IGNORECASE)
            texto_limpio = re.sub(r'</strong>', '</b>', texto_limpio, flags=re.IGNORECASE)
            
            # Convertir etiquetas de cursiva HTML a formato ReportLab
            texto_limpio = re.sub(r'<em>', '<i>', texto_limpio, flags=re.IGNORECASE)
            texto_limpio = re.sub(r'</em>', '</i>', texto_limpio, flags=re.IGNORECASE)
            
            # Remover otras etiquetas HTML pero mantener <b>, </b>, <i> y </i>
            texto_limpio = re.sub(r'<(?!/?[bi]\b)[^>]+>', '\n', texto_limpio)
            
            # Limpiar entidades HTML y &nbsp;
            texto_limpio = unescape(texto_limpio)
            texto_limpio = texto_limpio.replace('\xa0', ' ')
            
            # Crear estilo justificado
            estilo_justificado = ParagraphStyle(
                'justificado',
                parent=estilo_normal,
                fontName='DejaVu',
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY,
                spaceAfter=10
            )
            
            # Dividir en párrafos (doble salto de línea o más)
            parrafos = re.split(r'\n\s*\n', texto_limpio)
            
            for parrafo in parrafos:
                # Limpiar espacios y unir líneas del mismo párrafo
                lineas = [line.strip() for line in parrafo.splitlines() if line.strip()]
                if lineas:
                    texto_parrafo = ' '.join(lineas)
                    # Escapar solo & pero mantener las etiquetas <b> e <i>
                    texto_parrafo = texto_parrafo.replace('&', '&amp;')
                    elementos.append(Paragraph(texto_parrafo, estilo_justificado))
            
            elementos.append(Spacer(1, 0.3*inch))

        doc.build(elementos)
        pdf_value = buffer.getvalue()
        buffer.close()

        return request.make_response(
            pdf_value,
            headers=[('Content-Type','application/pdf'),('Content-Disposition',content_disposition(f"{receta.name}.pdf"))]
        )