# -*- coding: utf-8 -*-
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http

class MyCustomerPortal(CustomerPortal):

    def _get_optional_billing_fields(self):
        # Traemos la lista original
        optional_fields = super(MyCustomerPortal, self)._get_optional_billing_fields()
        
        # Agregamos tus campos extra
        # Nota: 'vat' suele venir por defecto, pero no hace daño dejarlo
        optional_fields.extend(['x_regimen_fiscal', 'x_uso_cfdi', 'vat'])
        
        return optional_fields