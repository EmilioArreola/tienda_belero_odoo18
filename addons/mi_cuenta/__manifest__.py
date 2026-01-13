# -*- coding: utf-8 -*-
{
    'name': "Mi Cuenta Personalización",
    'summary': "Vista simple con RFC y Régimen en el portal",
    'description': """
        Módulo para personalizar el portal del cliente:
        - Oculta el selector de formato electrónico (EDI).
        - Añade campos para RFC (vat) y Régimen Fiscal.
        - Cambia la etiqueta 'Nombre' por 'Razón Social'.
    """,
    'author': "SmApps",
    'category': 'Website/Portal',
    'version': '2.2',
    
    # DEPENDENCIAS:
    # 'portal': Para la vista base de detalles (nombre, email).
    # 'account': CRUCIAL para poder modificar/ocultar el campo 'invoice_edi_format'.
    'depends': ['portal', 'account'], 

    # VISTAS:
    'data': [
        'views/portal_add_fields.xml',  # El que acabamos de arreglar
    ],

    'installable': True,
    'application': False, # False porque es un módulo técnico/extensión, no una App principal
    'license': 'LGPL-3',
    'icon': '/mi_cuenta/static/description/icon.png',
}