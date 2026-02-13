# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SucursalesApiController(http.Controller):

    @http.route('/shop/update_sucursal', type='json', auth="public", website=True, csrf=False)
    def update_sucursal_recogida(self, sucursal=None, **kwargs):
        """
        Guarda la sucursal tanto en la sesión (memoria) como en la BD (disco).
        Es vital usar sudo() para garantizar que se guarde sin errores de permisos.
        """
        # 1. Guardar en sesión (Backup rápido para recuperación)
        request.session['sucursal_carrito_backup'] = sucursal
        
        # 2. Guardar en Base de Datos (Persistencia firme para el reporte PDF)
        order = request.website.sale_get_order(force_create=False)
        if order and sucursal:
            try:
                _logger.info(f"📍 Guardando sucursal '{sucursal}' en orden {order.name}")
                # IMPORTANTE: Usamos sudo() para saltar reglas de seguridad restrictivas
                # y asegurar que el dato se escriba sí o sí.
                order.sudo().write({'sucursal_recogida': sucursal})
                return {'status': 'success'}
            except Exception as e:
                _logger.error(f"❌ Error escribiendo sucursal: {e}")
                return {'status': 'error', 'message': str(e)}
        
        return {'status': 'no_order'}

    @http.route('/shop/get_sucursal', type='json', auth="public", website=True, csrf=False)
    def get_sucursal_recogida(self, **kwargs):
        # Intentamos obtener de la sesión primero
        val = request.session.get('sucursal_carrito_backup')
        
        # Si no hay en sesión, buscamos en la orden de la BD
        if not val:
            order = request.website.sale_get_order(force_create=False)
            if order:
                val = order.sudo().sucursal_recogida
        
        return {'status': 'success', 'sucursal': val}

    @http.route('/shop/es_recogida', type='json', auth="public", website=True, csrf=False)
    def check_es_recogida(self, carrier_id=None, **kwargs):
        if not carrier_id:
            return {'es_recogida': False}
        
        # Usamos sudo() para leer la configuración del envío sin problemas
        carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
        return {'es_recogida': carrier.exists() and carrier.es_recogida_tienda}