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
        ('sin_asignar', '⚠️ NO ASIGNADA (Error de Selección)'),
    ], string='📍 Sucursal de Recogida', 
       copy=False, 
       tracking=True)

    def _es_metodo_recogida(self):
        self.ensure_one()
        return self.carrier_id and self.carrier_id.es_recogida_tienda

    # -------------------------------------------------------------------------
    # EL ESCUDO PROTECTOR (NUEVO)
    # -------------------------------------------------------------------------
    def write(self, vals):
        """
        Sobrescribimos el método write para evitar que Odoo borre la sucursal
        accidentalmente al recalcular tarifas de envío.
        """
        # Si Odoo intenta poner la sucursal en False/Vacío...
        if 'sucursal_recogida' in vals and not vals['sucursal_recogida']:
            
            for order in self:
                # 1. ¿Ya teníamos una sucursal válida guardada?
                if order.sucursal_recogida and order.sucursal_recogida != 'sin_asignar':
                    
                    # 2. ¿Seguimos usando un método de envío de "Recogida"?
                    # (Si vals tiene carrier_id, revisamos el nuevo; si no, el actual)
                    carrier_id = vals.get('carrier_id') or order.carrier_id.id
                    
                    es_recogida = False
                    if carrier_id:
                        carrier = self.env['delivery.carrier'].browse(carrier_id)
                        es_recogida = carrier.es_recogida_tienda

                    if es_recogida:
                        # ¡ALERTA! Odoo quiere borrar la sucursal pero seguimos en modo recogida.
                        # ESTO ES LO QUE CAUSABA EL ERROR.
                        _logger.info(f"🛡️ PROTECCIÓN ACTIVA: Evitando borrado accidental de sucursal en Orden {order.name}")
                        # Eliminamos la orden de borrar del diccionario 'vals'
                        del vals['sucursal_recogida']
                        break # Salimos del loop, ya modificamos vals para todos

        return super(SaleOrder, self).write(vals)

    # -------------------------------------------------------------------------
    # VALIDACIÓN FINAL
    # -------------------------------------------------------------------------
    def action_confirm(self):
        for order in self:
            if order._es_metodo_recogida():
                
                # Intento de rescate desde sesión (por si acaso)
                if not order.sucursal_recogida and request:
                    try:
                        sucursal_backup = request.session.get('sucursal_carrito_backup')
                        if sucursal_backup:
                            order.sudo().write({'sucursal_recogida': sucursal_backup})
                    except: pass

                # Relectura forzosa
                order.invalidate_recordset(['sucursal_recogida'])
                
                # Validación final Anti-Crash
                if not order.sucursal_recogida:
                    # Si falla, asignamos valor de error pero DEJAMOS PASAR el pago
                    _logger.warning(f"⚠️ Orden {order.name} confirmada SIN sucursal.")
                    order.sudo().write({'sucursal_recogida': 'sin_asignar'})
                    
                    order.message_post(body=_(
                        "🛑 <b>¡ALERTA DE SISTEMA!</b><br/>"
                        "El cliente pagó pero la sucursal se perdió.<br/>"
                        "<b>Contactar al cliente inmediatamente.</b>"
                    ), message_type="comment", subtype_xmlid="mail.mt_note")

        return super(SaleOrder, self).action_confirm()