# -*- coding: utf-8 -*-
import logging
import re
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    # -------------------------------------------------------------------------
    # VALIDACIÓN DE FORTALEZA DE CONTRASEÑA
    # -------------------------------------------------------------------------
    def _validate_password_strength(self, password):
        """
        Valida la fortaleza de la contraseña según reglas personalizadas.
        Se llama desde create, write, change_password, etc.
        """
        if not password:
            return
        
        errors = []
        
        # Regla 1: Longitud Mínima de 8 caracteres
        if len(password) < 8:
            errors.append(_("• Debe tener al menos 8 caracteres"))
        
        # Regla 2: Al menos un número
        if not re.search(r'\d', password):
            errors.append(_("• Debe contener al menos un número (0-9)"))
        
        # Regla 3: Al menos una letra Mayúscula
        if not re.search(r'[A-Z]', password):
            errors.append(_("• Debe contener al menos una letra MAYÚSCULA"))
        
        # Regla 4: Al menos una letra Minúscula
        if not re.search(r'[a-z]', password):
            errors.append(_("• Debe contener al menos una letra minúscula"))
        
        # Regla 5 (OPCIONAL): Caracteres especiales
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        #     errors.append(_("• Debe contener al menos un carácter especial"))
        
        if errors:
            error_message = _("❌ La contraseña NO cumple con los requisitos de seguridad:\n\n") + "\n".join(errors)
            error_message += _("\n\n✅ Ejemplo válido: MiPassword123")
            raise UserError(error_message)

    @api.model
    def _check_password_policy(self, passwords):
        """ Método llamado al crear usuarios desde el backend. """
        result = super(ResUsers, self)._check_password_policy(passwords)
        
        if not isinstance(passwords, list):
            passwords = [passwords]
        
        for password in passwords:
            self._validate_password_strength(password)
        
        return result

    def write(self, vals):
        """ Intercepta CUALQUIER escritura (incluso cambios de admin). """
        if 'password' in vals and vals['password']:
            self._validate_password_strength(vals['password'])
        return super(ResUsers, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """ Intercepta la creación de nuevos usuarios. """
        for vals in vals_list:
            if 'password' in vals and vals['password']:
                self._validate_password_strength(vals['password'])
        return super(ResUsers, self).create(vals_list)
    
    def _set_password(self):
        """ Método de bajo nivel antes de establecer la contraseña cifrada. """
        for user in self:
            if hasattr(user, '_password') and user._password:
                self._validate_password_strength(user._password)
        return super(ResUsers, self)._set_password()

    def change_password(self, old_passwd, new_passwd):
        """
        Intercepta cuando un usuario cambia su PROPIA contraseña desde 'Preferencias'.
        """
        _logger.info(f"🔒 INTENTO DE CAMBIO DE CONTRASEÑA: Usuario {self.login}")
        
        # Validamos ANTES de que Odoo intente hacer el cambio
        try:
            self._validate_password_strength(new_passwd)
            _logger.info("✅ Contraseña validada correctamente")
        except UserError as e:
            _logger.warning(f"❌ Validación fallida: {str(e)}")
            raise e
        
        return super(ResUsers, self).change_password(old_passwd, new_passwd)

    # -------------------------------------------------------------------------
    # PLANTILLA DE CORREO PERSONALIZADA
    # -------------------------------------------------------------------------
    def _get_reset_password_url(self):
        """
        Genera la URL usando el método nativo de Odoo.
        No accede a campos ni columnas directamente para evitar errores de base de datos.
        """
        self.ensure_one()
        # Trabajamos con el partner (contacto) asociado al usuario
        partner = self.partner_id.sudo()
        
        # 1. Ordenamos a Odoo que prepare el token (donde sea que lo guarde)
        partner.signup_prepare(signup_type="reset")

        # 2. Le pedimos la URL completa (devuelve un diccionario {id: url})
        try:
            signup_urls = partner._get_signup_url_for_action(action='/web/reset_password')
            return signup_urls.get(partner.id, '#')
        except Exception as e:
            _logger.error(f"❌ Error generando URL de reseteo: {e}")
            # Fallback de emergencia solo si todo falla
            return f"{partner.get_base_url()}/web/reset_password?db={self.env.cr.dbname}"

    def action_reset_password(self):
        """
        Sobrescribe el método para usar la plantilla personalizada.
        CRÍTICO: Genera el token ANTES de enviar el correo.
        """
        # Evitar ejecución durante la instalación
        if self.env.context.get('install_mode', False):
            return

        # Validar que el usuario esté activo
        if self.filtered(lambda user: not user.active):
            raise UserError(_("No puedes restablecer la contraseña de usuarios archivados."))

        # ---------------------------------------------------------------------
        # 1. GENERAR TOKEN - ESTE ES EL PASO CRÍTICO
        # ---------------------------------------------------------------------
        # Esto crea el signup_token en el partner del usuario
        self.mapped('partner_id').sudo().signup_prepare(signup_type="reset")
        
        _logger.info(f"🔑 Token generado para: {self.mapped('login')}")

        # ---------------------------------------------------------------------
        # 2. BUSCAR LA PLANTILLA
        # ---------------------------------------------------------------------
        template = None
        
        if self.env.context.get('create_user'):
            # Para usuarios nuevos
            template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
        else:
            # Para reset de contraseña - Buscar plantilla personalizada
            try:
                # Intenta buscar por XML ID
                template = self.env.ref('personalizacion_correos.reset_password_email_custom', 
                                      raise_if_not_found=False)
                
                if template:
                    _logger.info("✅ Usando plantilla personalizada")
                else:
                    _logger.warning("⚠️ Plantilla personalizada no encontrada")
                    
            except Exception as e:
                _logger.warning(f"⚠️ Error buscando plantilla: {e}")
            
            # Fallback a la plantilla default de Odoo
            if not template:
                template = self.env.ref('auth_signup.reset_password_email', raise_if_not_found=False)
                _logger.info("ℹ️ Usando plantilla default de Odoo")

        # ---------------------------------------------------------------------
        # 3. ENVIAR CORREO
        # ---------------------------------------------------------------------
        if not template:
            raise UserError(_("No se encontró ninguna plantilla de correo para restablecer contraseña."))
        
        for user in self:
            if not user.email:
                raise UserError(_("El usuario %s no tiene un correo electrónico configurado.") % user.name)
            
            try:
                # force_send=False: Encola el correo (más rápido)
                # force_send=True: Envía inmediatamente (más lento pero más fácil de depurar)
                template.send_mail(user.id, force_send=True)
                _logger.info(f"📧 Correo de reset encolado para: {user.login} ({user.email})")
                
            except Exception as e:
                _logger.error(f"❌ Error enviando correo a {user.login}: {e}")
                raise UserError(_("Error al enviar el correo de restablecimiento. Por favor contacta al administrador."))

        return True