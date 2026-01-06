# -*- coding: utf-8 -*-
{
    'name': "Personalización de información del cliente en Mi cuenta",  # Puedes poner el nombre que quieras

    'summary': """
        Modifica los datos que le pide al cliente en su portal de usuario Mi cuenta.""",

    'description': """
        Este módulo hereda la vista del portal de cliente, elimina
        el selector de envío de facturasy agrega campos adicionales
        para que el cliente pueda subir su informaciópn de facuraciónn
        directamente desde su portal de usuario.
    """,
    'author': "Maharba",
    'category': 'Website/Portal',
    'version': '1.0',

    # DEPENDENCIAS:
    # Es VITAL poner 'portal' porque vamos a modificar una vista de ese módulo.
    # Si no lo pones, Odoo no encontrará la vista 'portal.portal_my_details'.
    'depends': ['portal','account'],

    # ARCHIVOS DE DATOS:
    # Aquí registramos el XML que creaste.
    'data': [
        'views/portal_templates.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}