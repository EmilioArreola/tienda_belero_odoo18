# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
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
    ], string='📍 Sucursal de Recogida', copy=False, tracking=True)

    def _es_metodo_recogida(self):
        """Verifica si el método de envío es de tipo recogida"""
        self.ensure_one()
        return self.carrier_id and self.carrier_id.es_recogida_tienda

    def action_confirm(self):
        """
        Sobrescribimos confirmar para:
        1. Rescatar la sucursal de la sesión si falta (para que salga en el PDF).
        2. Limpiar líneas duplicadas.
        """
        # 1. RESCATE DE SEGURIDAD
        # Si el usuario eligió sucursal en la web pero no se guardó en la BD,
        # la recuperamos de la cookie de sesión AQUÍ, justo antes de confirmar.
        if request and getattr(request, 'session', None):
            sucursal_backup = request.session.get('sucursal_carrito_backup')
            if sucursal_backup:
                # Solo aplicamos a órdenes que no tengan el dato
                for order in self:
                    if not order.sucursal_recogida:
                        _logger.info(f"🚑 [PDF Rescue] Guardando sucursal '{sucursal_backup}' en orden {order.name}")
                        order.sudo().write({'sucursal_recogida': sucursal_backup})

        # 2. LIMPIEZA DE DUPLICADOS
        for order in self:
            # Solo si es método de recogida
            if order._es_metodo_recogida():
                delivery_lines = order.order_line.filtered(lambda l: l.is_delivery)
                if len(delivery_lines) > 1:
                    # Si hay más de una línea de envío, borramos las sobras
                    delivery_lines[1:].unlink()

        return super(SaleOrder, self).action_confirm()