# -*- coding: utf-8 -*-
{
    'name': "Personalización de Reportes con Fecha",
    'summary': """
        Reemplaza la dirección de la compañía en los reportes
        por la fecha de impresión actual.""",
    'description': """
        Este módulo hereda el layout estándar de los reportes (facturas, cotizaciones, etc.)
        y cambia dinámicamente la dirección de la empresa por la fecha del día.
    """,
    'author': "Maharba",
    'website': "https://www.tuweb.com",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['web'],  # Depende del módulo 'web' porque modificamos una de sus plantillas
    'data': [
        'views/report_layout_override.xml', # Llama a nuestro archivo XML
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}