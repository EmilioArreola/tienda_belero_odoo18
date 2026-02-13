# -*- coding: utf-8 -*-
import logging
from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo.http import request 

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ============================================================
    # 1. HELPERS
    # ============================================================

    def _is_frontend_interaction(self):
        """Detecta si estamos en el Sitio Web."""
        if not request: return False
        if getattr(request, 'website', False): return True
        try:
            if hasattr(request, 'httprequest'):
                path = request.httprequest.path
                if '/shop' in path or '/payment' in path: return True
        except: pass
        return False

    def _get_pickup_carrier(self):
        return self.env['delivery.carrier'].search(
            [('name', 'ilike', 'Recoger en tienda')], limit=1
        )

    # ============================================================
    # 2. WRITE / CREATE (Lógica Backend)
    # ============================================================

    def write(self, vals):
        if self._is_frontend_interaction():
            return super().write(vals)

        res = super().write(vals)
        
        if self.env.context.get('skip_pickup_sync'): return res

        for order in self:
            if 'carrier_id' in vals:
                order.with_context(skip_pickup_sync=True)._sync_pickup_backend()
            elif 'order_line' in vals and not order.carrier_id:
                order.with_context(skip_pickup_sync=True)._sync_pickup_backend()

        return res

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        if self._is_frontend_interaction(): return orders

        for order in orders:
            if not order.carrier_id:
                order.with_context(skip_pickup_sync=True)._sync_pickup_backend()
        return orders

    # ============================================================
    # 3. SINCRONIZACIÓN AUTOMÁTICA (Backend)
    # ============================================================

    def _sync_pickup_backend(self):
        self.ensure_one()
        if self.state not in ['draft', 'sent']: return

        pickup_carrier = self._get_pickup_carrier()
        if not pickup_carrier: return

        current_delivery = self.order_line.filtered(
            lambda l: l.is_delivery and l.product_id == pickup_carrier.product_id
        )

        # Si el carrier es DIFERENTE a pickup, borrar línea
        if self.carrier_id and self.carrier_id != pickup_carrier:
            if current_delivery:
                current_delivery.with_context(skip_pickup_sync=True).unlink()
            return

        # Si el carrier ES pickup, asegurar línea
        has_products = any(
            not l.is_delivery and not l.display_type and l.product_id 
            for l in self.order_line
        )

        if has_products:
            if self.carrier_id != pickup_carrier:
                self.carrier_id = pickup_carrier.id
            
            if not current_delivery:
                self._create_pickup_line(pickup_carrier)
            elif len(current_delivery) > 1:
                # Limpieza de duplicados
                current_delivery[1:].with_context(skip_pickup_sync=True).unlink()

        else:
            if current_delivery:
                current_delivery.with_context(skip_pickup_sync=True).unlink()
            if self.carrier_id == pickup_carrier:
                self.carrier_id = False

    def _create_pickup_line(self, carrier):
        self.env['sale.order.line'].with_context(skip_pickup_sync=True).create({
            'order_id': self.id,
            'product_id': carrier.product_id.id,
            'name': carrier.name,
            'product_uom_qty': 1,
            'product_uom': carrier.product_id.uom_id.id,
            'price_unit': 0.0,
            'is_delivery': True,
            'sequence': 9999,
        })

    # ============================================================
    # 4. VALIDACIÓN Y RESCATE (CRÍTICO PARA REPORTES)
    # ============================================================

    def _enforce_pickup_validation(self):
        if self._is_frontend_interaction(): return

        for order in self:
            pickup_carrier = order._get_pickup_carrier()
            if pickup_carrier and order.carrier_id == pickup_carrier:
                if not order.sucursal_recogida:
                    raise ValidationError(_(
                        "🛑 ¡ACCIÓN REQUERIDA! (Backend)\n"
                        "Seleccione una sucursal de recogida."
                    ))

    def action_confirm(self):
        # --- A) OPERACIÓN DE RESCATE ---
        # Si venimos del sitio web y el campo está vacío, lo recuperamos de la sesión.
        # Esto asegura que el PDF salga correcto.
        if request and getattr(request, 'session', None):
            for order in self:
                if not order.sucursal_recogida:
                    sucursal = request.session.get('sucursal_carrito_backup')
                    if sucursal:
                        _logger.info(f"🚑 RESTAURANDO sucursal desde sesión: {sucursal}")
                        order.sudo().write({'sucursal_recogida': sucursal})
        
        # --- B) Validación Backend ---
        self._enforce_pickup_validation()
        
        return super().action_confirm()

    def action_quotation_send(self):
        self._enforce_pickup_validation()
        return super().action_quotation_send()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def unlink(self):
        orders = self.mapped('order_id')
        res = super().unlink()
        if request and getattr(request, 'website', False): return res
        if not self.env.context.get('skip_pickup_sync'):
            for order in orders:
                order.with_context(skip_pickup_sync=True)._sync_pickup_backend()
        return res