{
    'name': 'Validación de Usuarios Únicos',
    'version': '18.0.1.0.0',
    'summary': 'Evita la creación de usuarios con datos duplicados (Email/DNI)',
    'category': 'Administration',
    'author': 'SmApps',
    'depends': ['base','contacts','website_sale',],
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'icon': '/validacion_usuario_unico/static/description/icon.png',
}