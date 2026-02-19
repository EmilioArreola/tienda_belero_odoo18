from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal

class BeleroCustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/toggle_tax'], type='http', auth="public", website=True)
    def portal_order_toggle_tax(self, order_id, access_token=None, tax_mode='on', **kw):
        # Validamos el acceso para que nadie edite órdenes ajenas
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except Exception:
            return request.redirect('/my')

        # Guardamos la elección en la base de datos
        order_sudo.sudo().write({'belero_tax_mode': tax_mode})
        
        # Regresamos a la orden con la nueva vista
        return request.redirect(order_sudo.get_portal_url())