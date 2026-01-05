# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sucursal_recogida = fields.Selection([
        ('escuadron_201', 'Escuadrón 201'),
        ('lazaro_cardenas', 'Av. Lázaro Cárdenas'),
        ('cosijoeza', 'Calle Cosijoeza'),
        ('eucaliptos', 'Eucaliptos (Reforma)'),
        ('riveras', 'Riveras del Atoyac'),
        ('diaz_ordaz', 'Díaz Ordaz (Centro)'),
        ('eduardo_mata', 'Av. Eduardo Mata'),
        ('cristobal_colon', 'Carretera Cristóbal Colón'),
        ('yagul', 'Calle Yagul'),
        ('vicente_guerrero', 'Vicente Guerrero'),
        ('sin_asignar', '⚠️ NO ASIGNADA (Error de Selección)'), # Opción de respaldo
    ], string='📍 Sucursal de Recogida', 
       copy=False, 
       tracking=True)

    def _es_metodo_recogida(self):
        self.ensure_one()
        return self.carrier_id and self.carrier_id.es_recogida_tienda

    def action_confirm(self):
        """
        Validación tolerante a fallos para evitar errores 500 tras el pago.
        """
        for order in self:
            if order._es_metodo_recogida():
                
                # 1. INTENTO DE RESCATE (Sesión)
                if not order.sucursal_recogida and request:
                    try:
                        sucursal_backup = request.session.get('sucursal_carrito_backup')
                        if sucursal_backup:
                            _logger.info(f"🚑 [RESCATE] Recuperando '{sucursal_backup}' desde Sesión.")
                            order.sudo().write({'sucursal_recogida': sucursal_backup})
                    except Exception as e:
                        _logger.error(f"Error accediendo a sesión: {e}")

                # 2. INTENTO DE RESCATE FINAL (Anti-Crash)
                # Forzamos lectura fresca de la DB
                order.invalidate_recordset(['sucursal_recogida'])
                
                if not order.sucursal_recogida:
                    # Si llegamos aquí, el pago YA SE HIZO o se está procesando.
                    # NO PODEMOS elevar un UserError porque rompería el flujo de pago (Error 500).
                    
                    _logger.warning(f"⚠️ Orden {order.name} confirmada SIN sucursal. Asignando valor por defecto.")
                    
                    # A. Asignamos un valor de 'error' para que no falle el campo required (si lo fuera)
                    # o simplemente dejamos constancia.
                    order.sudo().write({'sucursal_recogida': 'sin_asignar'})
                    
                    # B. Mandamos mensaje al CHATTER para avisar al humano
                    order.message_post(body=_(
                        "🛑 <b>¡ALERTA DE SISTEMA!</b><br/>"
                        "El cliente seleccionó 'Recoger en Tienda' pero la sucursal no se guardó correctamente.<br/>"
                        "El pedido ha sido confirmado para no interrumpir el pago, pero <b>debes contactar al cliente</b> para preguntar dónde recogerá."
                    ), message_type="comment", subtype_xmlid="mail.mt_note")

        return super(SaleOrder, self).action_confirm()