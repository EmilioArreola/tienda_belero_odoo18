# -*- coding: utf-8 -*-
import logging
from odoo import models, api, _, fields, Command
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # -------------------------------------------------------------------------
    # 1. AUTOMATISMO VISUAL (UI - Entrada Manual)
    # -------------------------------------------------------------------------
    @api.onchange('order_line', 'partner_id')
    def _onchange_auto_add_pickup_line(self):
        """
        Se dispara cada vez que modificas las líneas en pantalla.
        Se encarga de mostrar la línea de envío INMEDIATAMENTE.
        """
        # 1. Buscar el transportista
        pickup_carrier = self.env['delivery.carrier'].search([('name', 'ilike', 'Recoger en tienda')], limit=1)
        if not pickup_carrier:
            return

        # 2. ¿Tenemos productos reales en la lista actual?
        #    (Iteramos sobre las líneas en memoria, que pueden ser 'NewId')
        has_products = False
        delivery_line_exists = False
        
        for line in self.order_line:
            # Ignoramos notas/secciones
            if not line.display_type and line.product_id:
                if line.product_id == pickup_carrier.product_id:
                    delivery_line_exists = True
                else:
                    has_products = True

        # 3. Lógica de Acción
        if has_products:
            # A) Si el carrier no está puesto, lo ponemos
            if self.carrier_id != pickup_carrier:
                self.carrier_id = pickup_carrier.id
            
            # B) Si falta la línea visual, la agregamos
            if not delivery_line_exists:
                _logger.info("🚚 [UI] Agregando línea visual de envío...")
                
                # Preparamos los valores. IMPORTANTE: No pasar 'order_id' en onchange
                vals = {
                    'product_id': pickup_carrier.product_id.id,
                    'name': pickup_carrier.name,
                    'product_uom_qty': 1,
                    'product_uom': pickup_carrier.product_id.uom_id.id,
                    'price_unit': 0.0,
                    'is_delivery': True,
                    'sequence': 9999, # Intentamos que vaya al final
                }
                
                # Usamos Command.create (si tu Odoo es moderno) o new()
                # La forma más compatible con onchange es append directo con new
                self.order_line += self.env['sale.order.line'].new(vals)

    # -------------------------------------------------------------------------
    # 2. AYUDANTE DE BACKEND (Base de Datos)
    # -------------------------------------------------------------------------
    def _ensure_pickup_line_backend(self):
        """ Revisa la BD y crea la línea física si falta (Para Catálogo/Importación) """
        for order in self:
            if order.state not in ['draft', 'sent']: continue

            pickup_carrier = self.env['delivery.carrier'].sudo().search([('name', 'ilike', 'Recoger en tienda')], limit=1)
            if not pickup_carrier: continue

            # Verificar productos y existencia de línea en BD
            has_products = any(not l.display_type and l.product_id != pickup_carrier.product_id for l in order.order_line)
            delivery_exists = any(l.product_id == pickup_carrier.product_id for l in order.order_line)

            if has_products:
                if order.carrier_id != pickup_carrier:
                    order.carrier_id = pickup_carrier.id
                
                if not delivery_exists:
                    _logger.info(f"🚚 [DB] Creando línea física en orden {order.name}")
                    self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': pickup_carrier.product_id.id,
                        'name': pickup_carrier.name,
                        'product_uom_qty': 1,
                        'product_uom': pickup_carrier.product_id.uom_id.id,
                        'price_unit': 0.0,
                        'is_delivery': True,
                        'sequence': 9999,
                    })

    # -------------------------------------------------------------------------
    # 3. VALIDACIONES
    # -------------------------------------------------------------------------
    def _enforce_pickup_validation(self):
        for order in self:
            # Doble check antes de validar
            order._ensure_pickup_line_backend()
            
            if order.carrier_id and 'recoger' in order.carrier_id.name.lower():
                if not order.sucursal_recogida:
                    raise ValidationError(_(
                        "🛑 ¡ACCIÓN REQUERIDA!\n\n"
                        "El método de envío es 'Recoger en tienda'.\n"
                        "👉 Es OBLIGATORIO seleccionar la '📍 Sucursal de Recogida' en la pestaña 'Otra Información'."
                    ))

    def action_confirm(self):
        self._enforce_pickup_validation()
        return super(SaleOrder, self).action_confirm()

    def action_quotation_send(self):
        self._enforce_pickup_validation()
        return super(SaleOrder, self).action_quotation_send()


# =============================================================================
# INTERCEPTOR DE LÍNEAS (Específico para el Catálogo)
# =============================================================================
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        # 1. Creamos las líneas normalmente
        lines = super(SaleOrderLine, self).create(vals_list)
        
        # 2. Evitamos bucles si estamos creando la línea de envío
        if self.env.context.get('skip_pickup_check'):
            return lines

        # 3. Detectamos si esto viene de una acción manual en UI
        #    Si vals_list tiene 1 elemento y parece ser manual, confiamos en el onchange
        #    y evitamos duplicar la creación en backend inmediatamente.
        #    PERO para el catálogo (que manda varios), sí ejecutamos.
        
        is_catalog_or_bulk = len(vals_list) > 1 or self.env.context.get('params', {}).get('view_type') == 'list'
        
        # Siempre ejecutamos el backend check para asegurar, 
        # PERO el _ensure_pickup_line_backend ya revisa si existe 'delivery_exists'.
        # La clave es que el onchange visual se ejecute primero.
        
        orders = lines.mapped('order_id')
        for order in orders:
            order.with_context(skip_pickup_check=True)._ensure_pickup_line_backend()
            
        return lines

    def unlink(self):
        orders = self.mapped('order_id')
        res = super(SaleOrderLine, self).unlink()
        for order in orders:
             order.with_context(skip_pickup_check=True)._ensure_pickup_line_backend()
        return res