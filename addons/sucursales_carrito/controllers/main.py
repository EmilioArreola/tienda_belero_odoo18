# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

class SucursalCheckout(http.Controller):

    @http.route(['/shop/update_sucursal'], type='json', auth="public", website=True, csrf=False)
    def update_sucursal_recogida(self, sucursal=None, **kwargs):
        """
        Recibe la sucursal seleccionada desde el JS y la guarda en la orden de venta (cotización)
        """
        # Obtenemos la cotización actual de la sesión
        order = request.website.sale_get_order()
        if not order:
            return {'error': 'No sale order found'}

        # Escribimos el valor en la cotización
        # Si 'sucursal' es un string vacío, guardará False (limpiará el campo)
        try:
            order.write({'sucursal_recogida': sucursal or False})
            return {'status': 'success', 'sucursal_guardada': sucursal}
        except Exception as e:
            # Esto podría fallar si el valor de 'sucursal' no es válido
            return {'error': str(e)}

    # --- ¡ESTA ES LA FUNCIÓN QUE TE FALTA! ---
    @http.route(['/shop/get_sucursal'], type='json', auth="public", website=True)
    def get_sucursal_recogida(self, **kwargs):
        """
        Devuelve la sucursal guardada en la orden actual para que
        el JS pueda restaurarla al cargar la página.
        """
        order = request.website.sale_get_order()
        if order and order.sucursal_recogida:
            return {'status': 'success', 'sucursal': order.sucursal_recogida}
        # Si no hay orden o no hay sucursal, no devuelve nada
        return {'status': 'error', 'sucursal': False}
    @http.route(['/shop/es_recogida'], type='json', auth="public", website=True)
    def es_metodo_recogida(self, carrier_id=None, **kwargs):
        """
        Comprueba si un delivery_carrier_id es de tipo "recogida en tienda"
        y devuelve True o False.
        """
        if not carrier_id:
            return {'es_recogida': False}
        
        try:
            # Buscamos el método de envío en el backend
            carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
            
            if carrier.exists() and carrier.es_recogida_tienda:
                return {'es_recogida': True}
            else:
                return {'es_recogida': False}
        
        except Exception as e:
            # Si algo falla (ej. el ID no es un número), asumimos que no es recogida
            return {'es_recogida': False}