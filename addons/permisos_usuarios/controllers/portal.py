# -*- coding: utf-8 -*-
import re
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class CustomerPortalExtended(CustomerPortal):
    """
    Extiende el controlador del portal para validar cambios de contraseña
    """

    def _validate_password_policy(self, password):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad
        """
        _logger.info("Validando contraseña en controlador portal")
        
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
        
        # Regla 5 (OPCIONAL): Descomenta para obligar caracteres especiales
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        #     errors.append(_("• Debe contener al menos un carácter especial"))
        
        if errors:
            error_message = _("La contraseña no cumple con los requisitos de seguridad:\n\n") + "\n".join(errors)
            _logger.warning(f"Contraseña rechazada: {error_message}")
            raise UserError(error_message)
        
        _logger.info("Contraseña válida en controlador portal")
        return True

    @http.route(['/my/security'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def security(self, **post):
        """Sobrescribe la ruta de seguridad para validar contraseñas"""
        _logger.info("="*60)
        _logger.info("CONTROLADOR /my/security EJECUTADO")
        _logger.info(f"Método: {request.httprequest.method}")
        _logger.info(f"Datos POST: {list(post.keys())}")
        _logger.info("="*60)
        
        if request.httprequest.method == 'POST':
            # Validar la nueva contraseña si se está cambiando
            new_password = post.get('new_password')
            _logger.info(f"Nueva contraseña detectada: {'Sí' if new_password else 'No'}")
            
            if new_password:
                try:
                    self._validate_password_policy(new_password)
                except UserError as e:
                    # Renderizar la página con el error
                    _logger.error(f"Error de validación: {str(e)}")
                    values = self._prepare_portal_layout_values()
                    values['error'] = str(e)
                    return request.render("portal.portal_my_security", values)
        
        return super(CustomerPortalExtended, self).security(**post)