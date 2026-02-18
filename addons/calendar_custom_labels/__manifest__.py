{
    'name': 'Personalización de Etiquetas de Calendario',
    'version': '18.0.1.0.1',
    'author': 'SmApps',
    'depends': [
        'calendar',
        'google_calendar', # Agrégalo si lo tienes instalado, ayuda a evitar el error de carga
    ],
    'data': [
        'views/calendar_event_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'icon': '/replace_url_shop/static/description/icon.png',
}