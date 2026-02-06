# -*- coding: utf-8 -*-
import re
from odoo import models, api, _, exceptions
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _validate_password_strength(self, password):
        """
        Valida la fortaleza de la contraseña según reglas personalizadas.
        Este método se llama SIEMPRE que se cambie una contraseña.
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
        
        # Regla 5 (OPCIONAL): Al menos un carácter especial
        # Descomenta las siguientes líneas si quieres obligar a usar símbolos:
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        #     errors.append(_("• Debe contener al menos un carácter especial"))
        
        if errors:
            error_message = _("La contraseña NO cumple con los requisitos de seguridad:\n\n") + "\n".join(errors)
            error_message += _("\n\n\n Ejemplo de contraseña válida: MiPassword123")
            raise UserError(error_message)

    @api.model
    def _check_password_policy(self, passwords):
        """
        Método llamado al crear usuarios desde el backend.
        """
        result = super(ResUsers, self)._check_password_policy(passwords)
        
        if not isinstance(passwords, list):
            passwords = [passwords]
        
        for password in passwords:
            self._validate_password_strength(password)
        
        return result

    def write(self, vals):
        """
        Intercepta CUALQUIER escritura en el modelo res.users.
        Si se está cambiando la contraseña, la valida primero.
        """
        # Si se está actualizando la contraseña, validarla
        if 'password' in vals and vals['password']:
            self._validate_password_strength(vals['password'])
        
        return super(ResUsers, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Intercepta la creación de usuarios para validar contraseñas.
        """
        for vals in vals_list:
            if 'password' in vals and vals['password']:
                self._validate_password_strength(vals['password'])
        
        return super(ResUsers, self).create(vals_list)
    
    def _set_password(self):
        """
        Método adicional que se llama al cambiar contraseña.
        """
        # Validar antes de establecer la contraseña
        for user in self:
            if hasattr(user, '_password'):
                self._validate_password_strength(user._password)
        
        return super(ResUsers, self)._set_password()

    def change_password(self, old_passwd, new_passwd):
        """
        Método llamado cuando un usuario cambia su propia contraseña.
        Este es el método clave para el portal de usuarios.
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info("="*50)
        _logger.info(f"CAMBIO DE CONTRASEÑA DETECTADO")
        _logger.info(f"Usuario: {self.login} (ID: {self.id})")
        _logger.info(f"Nueva contraseña: {new_passwd}")
        _logger.info("="*50)
        
        # Validar la nueva contraseña ANTES de cambiarla
        # FORZAMOS la validación incluso para superadmin
        try:
            self._validate_password_strength(new_passwd)
            _logger.info("Contraseña validada correctamente")
        except UserError as e:
            _logger.error(f"Validación de contraseña falló: {str(e)}")
            raise
        
        return super(ResUsers, self).change_password(old_passwd, new_passwd)