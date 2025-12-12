{
    'name': 'Colores Custom',
    'version': '1.0',
    'category': 'Theme',
    'summary': 'Cambia el color del navbar y elimina el morado de Odoo',
    'author': 'Abraham',
    'depends': ['web'],
    'data': [
        'views/report_sale_custom.xml',
        'views/web_layout_custom.xml',
    ], 
    'assets': {
        'web.assets_backend': [
            'colores_custom/static/src/css/colores.css',
        ],
    },
    'installable': True,
    'application': False,
}
