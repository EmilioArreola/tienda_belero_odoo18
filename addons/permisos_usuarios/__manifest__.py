# -*- coding: utf-8 -*-
{
    'name': "Permisos Personalizados",
    'summary': "Agrega niveles de acceso extra para la gestión de Contactos.",
    'author': 'SmApps',
    'category': 'Administration',
    'version': '1.0',
    'license': 'LGPL-3',

    # Dependemos de 'contacts' para asegurarnos de que la App de Contactos esté instalada
    'depends': ['base', 'contacts', 'spreadsheet_dashboard', 'modulo_recetas', 'auth_signup', 'portal', 'sale', 'personalizacion_correos', 'delivery', 'sucursales_carrito'],

    # Cargamos solo el XML de seguridad
    'data': [
        'security/contactos.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'permisos_usuarios/static/src/js/copy_link.js',
        ],
    },

    'installable': True,
    'application': False, # False porque es un módulo técnico/
    'icon': '/permisos_usuarios/static/description/icon.png',
}