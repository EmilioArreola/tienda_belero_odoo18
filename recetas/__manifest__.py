# __manifest__.py
{
    'name': 'Recetas de Cocina',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Gestión de recetas con galería y pop-ups',
    'description': """
        Módulo para gestionar recetas de cocina con:
        - Galería visual de recetas
        - Pop-ups con detalle completo
        - Categorización y búsqueda
        - Interfaz moderna con OWL
    """,
    'author': 'Maharba',
    'depends': ['base', 'web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/receta_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'recetas/static/src/js/**/*',
            'recetas/static/src/xml/**/*',
            'recetas/static/src/css/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}


# Estructura de carpetas del módulo:
"""
recetas/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── receta.py
├── views/
│   └── receta_views.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        ├── js/
        │   └── recetas_galeria.js
        ├── xml/
        │   └── recetas_templates.xml
        └── css/
            └── recetas.css
"""

# __init__.py (raíz del módulo)
# from . import models

# models/__init__.py
# from . import receta