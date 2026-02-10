from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    global_max_discount = fields.Float(
        string="Descuento Máximo Global (%)",
        config_parameter='sale.global_max_discount',
        default=0.0
    )

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # --- CAMPO PRINCIPAL (Validación) ---
    product_max_discount = fields.Float(
        string="Desc. Máximo Actual",
        help="Valor usado para validar ventas. Se actualiza automáticamente."
    )

    # --- PRECIOS Y DESCUENTOS POR OPCIÓN ---
    price_1 = fields.Float(string='Precio 1')
    discount_1 = fields.Float(string='Desc. Máx 1')

    price_2 = fields.Float(string='Precio 2')
    discount_2 = fields.Float(string='Desc. Máx 2')
    
    price_3 = fields.Float(string='Precio 3')
    discount_3 = fields.Float(string='Desc. Máx 3')
    
    price_4 = fields.Float(string='Precio 4')
    discount_4 = fields.Float(string='Desc. Máx 4')

    # --- SELECTOR ---
    active_price_selector = fields.Selection([
        ('p1', 'Opción 1'),
        ('p2', 'Opción 2'),
        ('p3', 'Opción 3'),
        ('p4', 'Opción 4'),
    ], string="Selección de Tarifa", default='p1')

    # ---------------------------------------------------------
    # 1. LOGICA VISUAL (Para que el usuario lo vea al editar)
    # ---------------------------------------------------------
    @api.onchange('active_price_selector', 
                  'price_1', 'discount_1', 
                  'price_2', 'discount_2', 
                  'price_3', 'discount_3', 
                  'price_4', 'discount_4')
    def _onchange_update_public_config(self):
        """Actualiza la vista en tiempo real"""
        self._sync_prices_logic()

    # ---------------------------------------------------------
    # 2. LOGICA DE GUARDADO (El "Seguro" contra fallos)
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # Al crear, dejamos que Odoo guarde y luego forzamos la sincro
        products = super().create(vals_list)
        for product in products:
            product._sync_prices_db()
        return products

    def write(self, vals):
        # Primero guardamos los cambios
        res = super().write(vals)
        
        # Si se tocó algún precio o el selector, forzamos la actualización
        campos_relevantes = [
            'active_price_selector', 
            'price_1', 'discount_1',
            'price_2', 'discount_2',
            'price_3', 'discount_3',
            'price_4', 'discount_4'
        ]
        
        if any(field in vals for field in campos_relevantes):
            for product in self:
                product._sync_prices_db()
        
        return res

    # ---------------------------------------------------------
    # MÉTODOS AUXILIARES
    # ---------------------------------------------------------
    def _sync_prices_logic(self):
        """Lógica central de asignación"""
        if self.active_price_selector == 'p1':
            self.list_price = self.price_1
            self.product_max_discount = self.discount_1
        elif self.active_price_selector == 'p2':
            self.list_price = self.price_2
            self.product_max_discount = self.discount_2
        elif self.active_price_selector == 'p3':
            self.list_price = self.price_3
            self.product_max_discount = self.discount_3
        elif self.active_price_selector == 'p4':
            self.list_price = self.price_4
            self.product_max_discount = self.discount_4

    def _sync_prices_db(self):
        """Escribe en la base de datos sin crear bucles infinitos"""
        target_price = 0.0
        target_discount = 0.0
        
        if self.active_price_selector == 'p1':
            target_price = self.price_1
            target_discount = self.discount_1
        elif self.active_price_selector == 'p2':
            target_price = self.price_2
            target_discount = self.discount_2
        elif self.active_price_selector == 'p3':
            target_price = self.price_3
            target_discount = self.discount_3
        elif self.active_price_selector == 'p4':
            target_price = self.price_4
            target_discount = self.discount_4
            
        # Solo escribimos si los valores son diferentes para evitar recursión
        vals_to_write = {}
        if self.list_price != target_price:
            vals_to_write['list_price'] = target_price
        if self.product_max_discount != target_discount:
            vals_to_write['product_max_discount'] = target_discount
            
        if vals_to_write:
            # Usamos super().write para saltarnos nuestra propia validación y evitar loops
            super(ProductTemplate, self).write(vals_to_write)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    current_max_discount = fields.Float(
        string="% desc. limite",
        compute='_compute_max_discount',
        store=True  # Recomendado para mejor rendimiento
    )

    @api.depends('product_id', 'product_id.product_max_discount')
    def _compute_max_discount(self):
        global_limit = float(self.env['ir.config_parameter'].sudo().get_param('sale.global_max_discount', 0.0))
        for line in self:
            # Si el producto tiene un límite específico (>0), lo usamos.
            # Si no, usamos el global.
            if line.product_id.product_max_discount > 0:
                line.current_max_discount = line.product_id.product_max_discount
            else:
                line.current_max_discount = global_limit

    @api.constrains('discount', 'current_max_discount')
    def _check_discount_limit(self):
        for line in self:
            # Permitimos guardar si el descuento es 0, para no bloquear borradores iniciales
            if line.discount > 0 and line.discount > line.current_max_discount:
                origen = 'del Producto' if line.product_id.product_max_discount > 0 else 'Global'
                raise ValidationError(
                    f"¡Acción Bloqueada!\n"
                    f"El descuento del {line.discount}% supera el límite permitido de {line.current_max_discount}% "
                    f"establecido en la configuración {origen}."
                )