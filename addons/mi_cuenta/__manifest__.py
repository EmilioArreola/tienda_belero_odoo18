# -*- coding: utf-8 -*-
{
    'name': "Personalización de información del cliente en Mi cuenta",
    'summary': """Modifica los datos del portal Mi cuenta.""",
    'description': """Agrega RFC, Razón Social y Régimen Fiscal al portal.""",
    'author': "Abraham y Carla",
    'category': 'Website/Portal',
    'version': '1.2',
    # Agregamos 'l10n_mx_edi' para tener acceso al campo de Régimen Fiscal estándar
    'depends': ['portal', 'account', 'account_edi', 'l10n_mx_edi'],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}