# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sucursal_recogida = fields.Selection([
        # ... (tus sucursales, no cambian) ...
    ], string='Sucursal de Recogida', 
       copy=False,
       tracking=True,
       help="Sucursal donde el cliente recogerá su pedido")

    def _es_metodo_recogida(self):
        """
        Determina si el carrier actual es de tipo "recoger en tienda"
        basado en el campo booleano 'es_recogida_tienda' del método.
        """
        self.ensure_one()
        
        # Si no hay método de envío seleccionado, no es recogida
        if not self.carrier_id:
            return False
        
        # Devuelve directamente el valor del campo booleano
        # Esto es mucho más robusto que adivinar por el nombre o precio.
        return self.carrier_id.es_recogida_tienda

    def action_confirm(self):
        """
        Valida que haya sucursal seleccionada SOLO al momento de confirmar
        """
        for order in self:
            # La validación ahora usa la función corregida
            if order._es_metodo_recogida() and not order.sucursal_recogida:
                raise UserError(_(
                    'Debe seleccionar una sucursal de recogida antes de confirmar el pedido.\n\n'
                    'Por favor, regrese al paso anterior y seleccione la sucursal donde '
                    'desea recoger su pedido.'
                ))
        return super(SaleOrder, self).action_confirm()