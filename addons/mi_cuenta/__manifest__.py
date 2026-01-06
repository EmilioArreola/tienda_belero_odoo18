# -*- coding: utf-8 -*-
{
    'name': "Personalización de información del cliente en Mi cuenta",

    'summary': """
        Modifica los datos que le pide al cliente en su portal de usuario Mi cuenta.""",

    'description': """
        Este módulo hereda la vista del portal de cliente, elimina
        el selector de envío de facturas y agrega campos adicionales
        para que el cliente pueda subir su información de facturación
        directamente desde su portal de usuario.
    """,
    'author': "Maharba",
    'category': 'Website/Portal',
    'version': '1.1',

    # DEPENDENCIAS:
    # CORRECCIÓN IMPORTANTE: Agregamos 'account_edi' porque tu XML hereda de él.
    'depends': ['portal', 'account', 'account_edi'],

    # ARCHIVOS DE DATOS:
    'data': [
        'views/portal_templates.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}