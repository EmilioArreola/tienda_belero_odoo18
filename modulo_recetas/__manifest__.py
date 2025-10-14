# -*- coding: utf-8 -*-
{
    'name': "Módulo de Recetas",
    'summary': "Un módulo simple para gestionar un recetario de cocina.",
    'description': """
        Este módulo permite crear, ver y gestionar recetas de cocina.
        Muestra una vista resumida y una vista detallada al hacer clic.
    """,
    'author': "Tu Nombre",
    'website': "https://www.tuweb.com",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/recetas_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}