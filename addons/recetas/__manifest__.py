# __manifest__.py
{
    'name': 'Recetas de Cocina',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Gestión de recetas con galería y pop-ups en el sitio web',
    'author': 'Maharba',
    'depends': ['website'],
    'data': [
        'security/ir.model.access.csv',
        'views/receta_view.xml', # <-- Usando tu nombre de archivo (singular).
        'static/src/xml/recetas_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'recetas/static/src/css/recetas.css',
            'recetas/static/src/js/recetas_galeria.js',
        ],
    },
    'controllers': [
        'controllers/main.py',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}