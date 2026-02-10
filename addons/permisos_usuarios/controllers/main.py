# -*- coding: utf-8 -*-
import re
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)


class AuthSignupHomeExtended(AuthSignupHome):
    """
    Extiende el controlador de registro/cambio de contraseña 
    para aplicar la política de contraseñas personalizadas
    """

    def _validate_password_policy(self, password):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad
        """
        if not password:
            raise UserError(_("La contraseña no puede estar vacía."))
        
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
            error_message = _("La contraseña no cumple con los requisitos de seguridad:\n\n") + "\n".join(errors)
            raise UserError(error_message)
        
        return True

    @http.route()
    def web_auth_signup(self, *args, **kw):
        """Sobrescribe el método de registro para validar la contraseña"""
        if request.httprequest.method == 'POST':
            password = kw.get('password')
            if password:
                try:
                    self._validate_password_policy(password)
                except UserError as e:
                    qcontext = self.get_auth_signup_qcontext()
                    qcontext['error'] = str(e)
                    return request.render('auth_signup.signup', qcontext)
        
        return super(AuthSignupHomeExtended, self).web_auth_signup(*args, **kw)

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        """
        Sobrescribe el método de reset de contraseña.
        Maneja tanto la SOLICITUD de reset como el ESTABLECIMIENTO de nueva contraseña.
        """
        _logger.info("="*60)
        _logger.info("🌐 web_auth_reset_password ejecutado")
        _logger.info(f"Método: {request.httprequest.method}")
        _logger.info(f"Parámetros: {list(kw.keys())}")
        _logger.info("="*60)
        
        if request.httprequest.method == 'POST':
            # Si hay password, es el paso 2: establecer nueva contraseña
            password = kw.get('password')
            if password:
                _logger.info("📝 Validando nueva contraseña...")
                try:
                    self._validate_password_policy(password)
                    _logger.info("✅ Contraseña válida")
                except UserError as e:
                    _logger.error(f"❌ Contraseña inválida: {str(e)}")
                    qcontext = self.get_auth_signup_qcontext()
                    qcontext['error'] = str(e)
                    return request.render('auth_signup.reset_password', qcontext)
            
            # Si hay login/email pero no password, es el paso 1: solicitar reset
            login = kw.get('login')
            if login and not password:
                _logger.info(f"📧 Solicitando reset para: {login}")
        
        try:
            result = super(AuthSignupHomeExtended, self).web_auth_reset_password(*args, **kw)
            _logger.info("✅ Reset password exitoso")
            return result
        except Exception as e:
            _logger.error(f"❌ Error en reset password: {str(e)}")
            # Capturar el error y mostrar mensaje amigable
            qcontext = self.get_auth_signup_qcontext()
            qcontext['error'] = _("Hubo un error al procesar tu solicitud. Por favor intenta de nuevo.")
            return request.render('auth_signup.reset_password', qcontext)