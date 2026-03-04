# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class MyCustomerPortal(CustomerPortal):

    # Mantenemos las listas en caso de que alguna vista nativa de Odoo las necesite
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "x_regimen_fiscal", "x_uso_cfdi"]

    def _get_optional_billing_fields(self):
        return ["zipcode", "state_id", "vat", "company_name", "x_regimen_fiscal", "x_uso_cfdi"]

    # === LA SOLUCIÓN DEFINITIVA: Interceptamos la petición web directamente ===
    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        custom_data = {}
        
        # 1. Si el usuario dio clic en "Guardar" (POST), rescatamos nuestros datos
        # y los quitamos de 'post' para que el validador estricto de Odoo no los vea y no arroje error.
        if request.httprequest.method == 'POST':
            if 'x_regimen_fiscal' in post:
                custom_data['x_regimen_fiscal'] = post.pop('x_regimen_fiscal')
            if 'x_uso_cfdi' in post:
                custom_data['x_uso_cfdi'] = post.pop('x_uso_cfdi')

        # 2. Dejamos que Odoo ejecute toda su lógica normal (Nombre, Email, RFC, etc.)
        response = super(MyCustomerPortal, self).account(redirect=redirect, **post)

        # 3. Después de que Odoo termina, nosotros guardamos nuestros campos a la fuerza
        if request.httprequest.method == 'POST' and custom_data:
            # Si el usuario eligió "Seleccionar..." (vacío), enviamos False a la BD
            if not custom_data.get('x_regimen_fiscal'):
                custom_data['x_regimen_fiscal'] = False
            if not custom_data.get('x_uso_cfdi'):
                custom_data['x_uso_cfdi'] = False
            
            # Guardado maestro e irrefutable en el contacto del usuario
            request.env.user.partner_id.sudo().write(custom_data)

        return response