# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # 1. LISTA LIMPIA (Sin la opción de error)
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

    # -------------------------------------------------------------------------
    # EL ESCUDO PROTECTOR (Mantiene el dato seguro)
    # -------------------------------------------------------------------------
    def write(self, vals):
        if 'sucursal_recogida' in vals and not vals['sucursal_recogida']:
            for order in self:
                if order.sucursal_recogida: # Si ya tiene sucursal...
                    carrier_id = vals.get('carrier_id') or order.carrier_id.id
                    es_recogida = False
                    if carrier_id:
                        carrier = self.env['delivery.carrier'].browse(carrier_id)
                        es_recogida = carrier.es_recogida_tienda

                    if es_recogida:
                        # Ignoramos el borrado accidental de Odoo
                        del vals['sucursal_recogida']
                        break 
        return super(SaleOrder, self).write(vals)

    # -------------------------------------------------------------------------
    # VALIDACIÓN FINAL
    # -------------------------------------------------------------------------
    def action_confirm(self):
        for order in self:
            if order._es_metodo_recogida():
                
                # Intento de rescate desde sesión
                if not order.sucursal_recogida and request:
                    try:
                        sucursal_backup = request.session.get('sucursal_carrito_backup')
                        if sucursal_backup:
                            # Verificamos que el valor de respaldo sea válido en la lista nueva
                            # (para evitar errores si el respaldo era basura)
                            dict_sucursales = dict(self._fields['sucursal_recogida'].selection)
                            if sucursal_backup in dict_sucursales:
                                order.sudo().write({'sucursal_recogida': sucursal_backup})
                    except: pass

                # Relectura forzosa
                order.invalidate_recordset(['sucursal_recogida'])
                
                # Si sigue vacía, NO ponemos valor falso, simplemente avisamos en el chat.
                if not order.sucursal_recogida:
                    _logger.warning(f"⚠️ Orden {order.name} confirmada SIN sucursal.")
                    
                    # El mensaje rojo sigue siendo nuestra mejor alerta
                    order.message_post(body=_(
                        "🛑 <b>¡ALERTA DE SISTEMA!</b><br/>"
                        "El cliente pagó pero la sucursal no se seleccionó.<br/>"
                        "<b>Contactar al cliente inmediatamente.</b>"
                    ), message_type="comment", subtype_xmlid="mail.mt_note")

        return super(SaleOrder, self).action_confirm()