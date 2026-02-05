# -*- coding: utf-8 -*-
import re
from odoo import models, api, _, exceptions

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_password_policy(self, password):
        # 1. Validaciones básicas de Odoo (sin el módulo estricto)
        super(ResUsers, self)._check_password_policy(password)

        if not password:
            return

        # --- TUS REGLAS PERSONALIZADAS ---

        # Regla 1: Longitud Mínima (Reemplazando al módulo nativo)
        if len(password) < 8:
            raise exceptions.UserError(_("La contraseña es muy corta. Debe tener al menos 8 caracteres."))

        # Regla 2: Al menos un número
        if not re.search(r'\d', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos un número (0-9)."))

        # Regla 3: Al menos una letra Mayúscula
        if not re.search(r'[A-Z]', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos una letra MAYÚSCULA."))

        # Regla 4: Al menos una letra Minúscula
        if not re.search(r'[a-z]', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos una letra minúscula."))
        
        # OJO: En tu código anterior tenías activada la regla de caracteres especiales (!@#$).
        # Si NO quieres obligar a poner símbolos, comenta estas dos líneas:
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     raise exceptions.UserError(_("La contraseña debe contener al menos un carácter especial."))