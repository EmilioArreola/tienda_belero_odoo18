# -*- coding: utf-8 -*-
{
    'name': "Mi Cuenta Personalización",
    'summary': "Vista simple con RFC y Régimen",
    'description': "Módulo visual para modificar el portal.",
    'author': "Abraham y Carla",
    'category': 'Website/Portal',
    'version': '1.0',
    
    # Solo dependemos del portal base
    'depends': ['portal', 'account'], 

    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}