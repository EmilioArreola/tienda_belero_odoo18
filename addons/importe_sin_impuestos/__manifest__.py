{
    'name': 'Configuración de impuestos en importes',
    'version': '18.0.1.0.0',
    'summary': 'Configuración global para mostrar importes con o sin impuestos',
    'category': 'Sales',
    'author': 'SmApps',
    'depends': ['sale', 'base'],
    'data': [
        'views/res_config_settings_views.xml',
        'report/sale_report_templates.xml',
        'views/sale_portal_templates.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'icon': '/replace_url_shop/static/description/icon.png',

}