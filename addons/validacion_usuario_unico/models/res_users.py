from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            email = vals.get('email', '').strip() if vals.get('email') else False
            vat = vals.get('vat', '').strip() if vals.get('vat') else False
            
            if (email or vat) and not vals.get('parent_id'):
                # Construcción dinámica para evitar errores de sintaxis
                domain = []
                if email and vat:
                    domain = ['|', ('email', '=ilike', email), ('vat', '=', vat)]
                elif email:
                    domain = [('email', '=ilike', email)]
                elif vat:
                    domain = [('vat', '=', vat)]

                if domain:
                    search_domain = [('parent_id', '=', False), ('type', '=', 'contact')] + domain
                    existing_parent = self.search(search_domain, limit=1)

                    if existing_parent:
                        vals['parent_id'] = existing_parent.id
                        # CAMBIO CLAVE: Forzamos que sea un individuo y tipo delivery
                        vals['is_company'] = False
                        if vals.get('type') in ['contact', False]:
                            vals['type'] = 'delivery'
                        
                        if not vals.get('name') or vals.get('name') == existing_parent.name:
                            vals['name'] = _("Dirección adicional")

        return super(ResPartner, self).create(vals_list)

    @api.constrains('email', 'vat')
    def _check_unique_partner_data(self):
        for record in self:
            # Si tiene padre o es dirección, ignoramos la validación de "Único"
            if record.parent_id or record.type in ['delivery', 'invoice', 'other']:
                continue

            if record.email:
                duplicate = self.search([
                    ('id', '!=', record.id),
                    ('email', '=ilike', record.email.strip()),
                    ('type', '=', 'contact'),
                    ('parent_id', '=', False)
                ], limit=1)
                if duplicate:
                    raise ValidationError(_("Ya existe un contacto principal con el correo: %s") % record.email)

            if record.vat:
                duplicate_vat = self.search([
                    ('id', '!=', record.id),
                    ('vat', '=', record.vat.strip()),
                    ('type', '=', 'contact'),
                    ('parent_id', '=', False)
                ], limit=1)
                if duplicate_vat:
                    raise ValidationError(_("El número de identificación %s ya está en uso.") % record.vat)