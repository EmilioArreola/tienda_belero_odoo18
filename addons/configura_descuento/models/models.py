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

    product_max_discount = fields.Float(
        string="Desc. Máximo Específico",
        help="Si se establece mayor a 0, este valor tendrá prioridad sobre el límite global."
    )

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
            # Si el producto tiene configuración específica (>0), se usa esa.
            # Si es 0, hereda la global (que podría ser 0).
            if line.product_id.product_max_discount > 0:
                line.current_max_discount = line.product_id.product_max_discount
            else:
                line.current_max_discount = global_limit

    @api.constrains('discount', 'current_max_discount')
    def _check_discount_limit(self):
        for line in self:
            limit = line.current_max_discount
            
            # CAMBIO AQUÍ: Quitamos "limit > 0"
            # Ahora, si el límite es 0.0 y el descuento es 5.0, entrará al error.
            if line.discount > limit:
                # Determinamos qué regla causó el bloqueo para el mensaje
                origen = 'Producto' if line.product_id.product_max_discount > 0 else 'Global'
                
                raise ValidationError(
                    f"El descuento del {line.discount}% supera el límite permitido de {limit}% "
                    f"(Regla aplicada: {origen})."
                )