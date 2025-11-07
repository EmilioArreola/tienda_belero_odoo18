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