from odoo.addons.portal.controllers.portal import CustomerPortal

class MyCustomerPortal(CustomerPortal):

    def _get_optional_billing_fields(self):
        fields = super()._get_optional_billing_fields()
        fields += ['x_regimen_fiscal', 'x_uso_cfdi']
        return fields
