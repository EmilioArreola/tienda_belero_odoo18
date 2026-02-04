# -*- coding: utf-8 -*-
import re
from odoo import models, api, _, exceptions

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_password_policy(self, password):
        # 1. Ejecutar primero la validación nativa de Odoo (Longitud mínima configurada)
        super(ResUsers, self)._check_password_policy(password)

        # 2. Nuestras Validaciones de Complejidad
        if not password:
            return

        # Regla A: Al menos un número
        if not re.search(r'\d', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos un número (0-9)."))

        # Regla B: Al menos una letra Mayúscula
        if not re.search(r'[A-Z]', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos una letra MAYÚSCULA."))

        # Regla C: Al menos una letra Minúscula
        if not re.search(r'[a-z]', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos una letra minúscula."))

        # Regla D (Opcional): Al menos un carácter especial (@, #, $, etc)
        # Descomenta las siguientes líneas si quieres ser muy estricto:
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise exceptions.UserError(_("La contraseña debe contener al menos un carácter especial."))