# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request

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
    ], string='📍 Sucursal de Recogida', 
       copy=False, 
       tracking=True)

    def _es_metodo_recogida(self):
        self.ensure_one()
        return self.carrier_id and self.carrier_id.es_recogida_tienda

    def action_confirm(self):
        """
        Validación inteligente con rescate desde sesión.
        """
        for order in self:
            if order._es_metodo_recogida():
                
                # ---------------------------------------------------------
                # PLAN B: RESCATE DESDE LA SESIÓN
                # ---------------------------------------------------------
                # Si en la DB está vacío, miramos la memoria del navegador (sesión)
                if not order.sucursal_recogida and request:
                    sucursal_backup = request.session.get('sucursal_carrito_backup')
                    if sucursal_backup:
                        print(f"🚑 [RESCATE] Recuperando '{sucursal_backup}' desde la Sesión para Orden {order.id}")
                        order.sudo().write({'sucursal_recogida': sucursal_backup})
                
                # ---------------------------------------------------------
                # VALIDACIÓN FINAL
                # ---------------------------------------------------------
                # Forzamos relectura para ver si el rescate funcionó
                # (invalidate_recordset es vital en Odoo 18)
                order.invalidate_recordset(['sucursal_recogida'])
                
                if not order.sucursal_recogida:
                    raise UserError(_(
                        '⚠️ ¡Falta información!\n\n'
                        'Elegiste "Recoger en Tienda", pero no seleccionaste la sucursal.\n'
                        'Por favor selecciona una sucursal nuevamente.'
                    ))

        return super(SaleOrder, self).action_confirm()