# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SucursalesApiController(http.Controller):

    @http.route(['/shop/update_sucursal'], type='json', auth="public", website=True, csrf=False)
    def update_sucursal_recogida(self, sucursal=None, **kwargs):
        """
        API simple: Guarda en sesión (ram) y base de datos (disco).
        """
        try:
            # 1. SIEMPRE guardar en la sesión (Nuestra copia de seguridad)
            request.session['sucursal_carrito_backup'] = sucursal
            
            # 2. Intentar guardar en la Orden
            order = request.website.sale_get_order(force_create=False)
            if order:
                # Usamos sudo() para evitar reglas de registro
                order.sudo().write({'sucursal_recogida': sucursal})
                # Intentamos forzar el guardado, pero si falla, no importa, tenemos la sesión
                request.env.cr.commit()
                return {'status': 'success', 'message': 'Guardado OK'}
            
            return {'status': 'success', 'message': 'Guardado solo en sesión (Sin orden)'}

        except Exception as e:
            _logger.error(f"⚠️ Error en API update_sucursal: {str(e)}")
            # Devolvemos success porque al menos quedó en la sesión
            return {'status': 'success', 'message': 'Error en DB, salvado en sesión'}

    @http.route(['/shop/get_sucursal'], type='json', auth="public", website=True, csrf=False)
    def get_sucursal_recogida(self, **kwargs):
        """
        Recupera el dato para mostrarlo en el selector al recargar.
        """
        try:
            # Prioridad: Sesión (es lo más fresco)
            val = request.session.get('sucursal_carrito_backup')
            
            # Si no hay sesión, miramos la base de datos
            if not val:
                order = request.website.sale_get_order(force_create=False)
                if order:
                    val = order.sudo().sucursal_recogida
            
            return {'status': 'success', 'sucursal': val}
        except Exception:
            return {'status': 'success', 'sucursal': False}

    @http.route(['/shop/es_recogida'], type='json', auth="public", website=True, csrf=False)
    def check_es_recogida(self, carrier_id=None, **kwargs):
        try:
            if not carrier_id: return {'es_recogida': False}
            carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
            return {'es_recogida': carrier.exists() and carrier.es_recogida_tienda}
        except Exception:
            return {'es_recogida': False}