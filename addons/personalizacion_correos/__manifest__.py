{
    'name': "Diseño de Correos de Cambio de Contraseña",
    'summary': "Personaliza los correos de restablecimiento de contraseña con las nuevas reglas.",
    'author': 'SmApps',
    'version': '1.0',
    'depends': ['base', 'auth_signup'], # Importante: Depende de auth_signup
    'data': [
        'data/mail_template.xml',
    ],
    'installable': True,
    'application': False,
    'icon': '/personalizacion_correos/static/description/icon.png',
}