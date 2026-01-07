# -*- coding: utf-8 -*-
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class MyCustomerPortal(CustomerPortal):

    def _get_optional_billing_fields(self):
        optional_fields = super()._get_optional_billing_fields()
        return optional_fields + ['vat', 'x_regimen_fiscal']

    def details_form_validate(self, data):
        errors, error_msg = super().details_form_validate(data)

        # Aquí puedes validar si quieres:
        # if not data.get('x_regimen_fiscal'):
        #     errors['x_regimen_fiscal'] = 'missing'
        #     error_msg.append('Debes indicar tu régimen fiscal.')

        return errors, error_msg

    def details_form_save(self, data):
        # Dejamos que Odoo prepare los valores normales
        res = super().details_form_save(data)

        # Forzamos guardar nuestros campos custom
        partner = request.env.user.partner_id

        vals = {}
        if 'x_regimen_fiscal' in data:
            vals['x_regimen_fiscal'] = data.get('x_regimen_fiscal')
        if 'vat' in data:
            vals['vat'] = data.get('vat')

        if vals:
            partner.sudo().write(vals)

        return res
