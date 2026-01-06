# -*- coding: utf-8 -*-
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class MyPortal(CustomerPortal):

    # Esta función define qué campos son OBLIGATORIOS
    def _get_mandatory_billing_fields(self):
        fields = super(MyPortal, self)._get_mandatory_billing_fields()
        # Agregamos RFC (vat) y Régimen a obligatorios
        return fields + ['vat', 'l10n_mx_edi_fiscal_regime']

    # Esta función define qué campos son OPCIONALES (pero permitidos)
    def _get_optional_billing_fields(self):
        fields = super(MyPortal, self)._get_optional_billing_fields()
        # Puedes mover 'vat' o 'l10n_mx_edi_fiscal_regime' aquí si no quieres que sean obligatorios
        return fields