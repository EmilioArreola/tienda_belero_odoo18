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

    # --- CAMPO PRINCIPAL DE VALIDACIÓN (Lo que lee Ventas) ---
    product_max_discount = fields.Float(
        string="Desc. Máximo Actual",
        help="Este es el valor que se usa para validar las ventas. Se actualiza automáticamente al elegir un precio abajo."
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
    ], string="Selección de Tarifa", default='p1', 
       help="Al cambiar esto, se actualiza el Precio Público y el Descuento Máximo.")

    # --- LÓGICA DE ACTUALIZACIÓN ---
    @api.onchange('active_price_selector', 
                  'price_1', 'discount_1', 
                  'price_2', 'discount_2', 
                  'price_3', 'discount_3', 
                  'price_4', 'discount_4')
    def _onchange_update_public_config(self):
        """Actualiza Precio y Descuento Máximo según la opción elegida"""
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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    current_max_discount = fields.Float(
        string="% desc. limite",
        compute='_compute_max_discount'
    )

    @api.depends('product_id', 'discount')
    def _compute_max_discount(self):
        global_limit = float(self.env['ir.config_parameter'].sudo().get_param('sale.global_max_discount', 0.0))
        for line in self:
            # Usa el product_max_discount (que ya se actualizó automáticamente en el producto)
            if line.product_id.product_max_discount > 0:
                line.current_max_discount = line.product_id.product_max_discount
            else:
                line.current_max_discount = global_limit

    @api.constrains('discount', 'current_max_discount')
    def _check_discount_limit(self):
        for line in self:
            limit = line.current_max_discount
            if line.discount > limit:
                origen = 'Producto' if line.product_id.product_max_discount > 0 else 'Global'
                raise ValidationError(
                    f"El descuento del {line.discount}% supera el límite permitido de {limit}% "
                    f"(Regla aplicada: {origen})."
                )