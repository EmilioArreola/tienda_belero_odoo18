{
    'name': "Mi Cuenta Personalización",
    'summary': "Campos fiscales en portal cliente",
    'description': "Añade RFC, Régimen Fiscal y Uso CFDI al portal.",
    'author': "SmApps",
    'category': 'Website/Portal',
    'version': '3.0',

    'depends': ['portal'],

    'data': [
        'views/portal_extend.xml',
    ],

    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'icon': '/mi_cuenta/static/description/icon.png',
}
