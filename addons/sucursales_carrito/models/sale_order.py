# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sucursal_recogida = fields.Selection([
        ('escuadron_201', 'Escuadrón 201 #300, Antiguo Aereopuerto'),
        ('lazaro_cardenas', 'Av Lázaro Cárdenas 503-3, Col. Guelatao, Santa Lucía'),
        ('cosijoeza', 'Calle Cosijoeza #216-A, Barrio de Jalatlaco'),
        ('eucaliptos', 'Eucaliptos #215 В, Col. Reforma, 68050'),
        ('riveras', 'Libramiento Riveras del Atoyac #122-2'),
        ('diaz_ordaz', 'Díaz Ordaz #710, Col. Centro'),
        ('eduardo_mata', 'Av. Eduardo Mata #2302, Periférico'),
        ('cristobal_colon', 'Carretera Cristóbal Colón #202, Santa Rosa'),
        ('yagul', 'Calle Yagul esq. Cosijopi #122-A'),
        ('vicente_guerrero', 'Vicente Guerrero, Centro, Oaxaca'),
    ], string='Sucursal de Recogida', 
       copy=False,
       tracking=True,  # Para seguimiento en el chatter
       help="Sucursal donde el cliente recogerá su pedido")

    @api.constrains('sucursal_recogida', 'carrier_id')
    def _check_sucursal_recogida(self):
        """Valida que se haya seleccionado una sucursal si el método de entrega lo requiere"""
        for order in self:
            # Verifica si es un método de "recoger en tienda"
            # Ajusta esta lógica según tu configuración específica
            if order.carrier_id and self._es_metodo_recogida(order.carrier_id):
                if not order.sucursal_recogida:
                    raise ValidationError(_(
                        'Debe seleccionar una sucursal de recogida para este método de entrega.'
                    ))

    def _es_metodo_recogida(self, carrier):
        """
        Determina si un carrier es de tipo "recoger en tienda"
        Personaliza esta lógica según tus necesidades
        """
        # Opción 1: Por nombre del carrier
        if carrier.name and any(palabra in carrier.name.lower() 
                               for palabra in ['recoger', 'tienda', 'sucursal', 'pickup']):
            return True
        
        # Opción 2: Por tipo de entrega (si usas fixed para recogida)
        if carrier.delivery_type == 'fixed' and carrier.fixed_price == 0:
            return True
        
        # Opción 3: Agregar un campo personalizado al carrier (recomendado)
        # if hasattr(carrier, 'es_recogida_tienda') and carrier.es_recogida_tienda:
        #     return True
        
        return False

    def action_confirm(self):
        """Valida que haya sucursal seleccionada antes de confirmar"""
        for order in self:
            if order.carrier_id and self._es_metodo_recogida(order.carrier_id):
                if not order.sucursal_recogida:
                    raise ValidationError(_(
                        'Debe seleccionar una sucursal de recogida antes de confirmar el pedido.'
                    ))
        return super(SaleOrder, self).action_confirm()

    def _cart_update_order_line(self, product_id, quantity, order_line, **kwargs):
        """
        Override para mantener la sucursal al actualizar líneas del carrito
        """
        values = super()._cart_update_order_line(product_id, quantity, order_line, **kwargs)
        
        # Limpia la sucursal si se cambia a un método que no es de recogida
        if self.carrier_id and not self._es_metodo_recogida(self.carrier_id):
            if self.sucursal_recogida:
                self.sucursal_recogida = False
        
        return values