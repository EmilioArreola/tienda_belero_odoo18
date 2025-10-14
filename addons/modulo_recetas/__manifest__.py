# -*- coding: utf-8 -*-
{
    'name': "Módulo de Recetas",
    'summary': "Un recetario de cocina integrado con tu sitio web de Odoo.",
    'author': "Maharba",
    'category': 'Website',
    'version': '1.3', # Incrementa la versión
    'license': 'LGPL-3',

    'depends': ['base', 'website'],

    'data': [
        'security/ir.model.access.csv',
        'views/recetas_views.xml',
        'views/recetas_templates.xml',
    ],
     'assets': {
        'web.assets_frontend': [
            'modulo_recetas/static/src/css/recetas_styles.css',
        ],
    },


    'installable': True,
    'application': True,
    'auto_install': False,
}