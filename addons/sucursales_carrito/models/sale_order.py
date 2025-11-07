# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

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
       tracking=True,
       help="Sucursal donde el cliente recogerá su pedido")

    def _es_metodo_recogida(self):
        """
        Determina si el carrier actual es de tipo "recoger en tienda"
        """
        self.ensure_one()
        if not self.carrier_id:
            return False
        
        carrier = self.carrier_id
        
        # Opción 1: Por nombre del carrier
        if carrier.name and any(palabra in carrier.name.lower() 
                               for palabra in ['recoger', 'tienda', 'sucursal', 'pickup', 'retirar']):
            return True
        
        # Opción 2: Por tipo de entrega fixed con precio 0
        if carrier.delivery_type == 'fixed' and carrier.fixed_price == 0:
            return True
        
        return False

    def action_confirm(self):
        """
        Valida que haya sucursal seleccionada SOLO al momento de confirmar
        """
        for order in self:
            if order._es_metodo_recogida() and not order.sucursal_recogida:
                raise UserError(_(
                    'Debe seleccionar una sucursal de recogida antes de confirmar el pedido.\n\n'
                    'Por favor, regrese al paso anterior y seleccione la sucursal donde '
                    'desea recoger su pedido.'
                ))
        return super(SaleOrder, self).action_confirm()