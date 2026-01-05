# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SucursalesApiController(http.Controller):

    @http.route('/shop/update_sucursal', type='json', auth="public", website=True, csrf=False)
    def update_sucursal_recogida(self, sucursal=None, **kwargs):
        """
        Guarda la sucursal.
        """
        # Guardar en sesión siempre
        request.session['sucursal_carrito_backup'] = sucursal
        
        response = {'status': 'success'}
        
        # Intentar guardar en DB
        order = request.website.sale_get_order(force_create=False)
        if order:
            try:
                # Usamos sudo() y commit() para asegurar persistencia inmediata
                order.sudo().write({'sucursal_recogida': sucursal})
                request.env.cr.commit() 
                response['message'] = f"Guardado en ID {order.id}"
            except Exception as e:
                _logger.error(f"Error escribiendo sucursal: {e}")
                response['status'] = 'warning'
                response['error'] = str(e)
        else:
            response['message'] = "Sin orden activa"

        return response

    # (Mantén las otras funciones get_sucursal y check_es_recogida igual que antes)
    @http.route('/shop/get_sucursal', type='json', auth="public", website=True, csrf=False)
    def get_sucursal_recogida(self, **kwargs):
        val = request.session.get('sucursal_carrito_backup')
        if not val:
            order = request.website.sale_get_order(force_create=False)
            if order: val = order.sudo().sucursal_recogida
        return {'status': 'success', 'sucursal': val}

    @http.route('/shop/es_recogida', type='json', auth="public", website=True, csrf=False)
    def check_es_recogida(self, carrier_id=None, **kwargs):
        if not carrier_id: return {'es_recogida': False}
        carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
        return {'es_recogida': carrier.exists() and carrier.es_recogida_tienda}