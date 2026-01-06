# -*- coding: utf-8 -*-
{
    'name': "Personalización de Portal",  # Puedes poner el nombre que quieras

    'summary': """
        Oculta el campo de 'Formato electrónico' en el perfil del cliente.
    """,

    'description': """
        Este módulo hereda la vista del portal de cliente y elimina
        el selector de envío de facturas.
    """,

    'author': "Maharba",
    'website': "http://www.tuweb.com",
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