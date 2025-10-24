# -*- coding: utf-8 -*-
{
    'name': "Mis Personalizaciones (Reportes y Web)",
    'summary': """
        Ajustes personalizados para reportes y la interfaz web.""",
    'description': """
        - Reemplaza la dirección en reportes por la fecha de impresión.
        - Elimina la marca "Con la tecnología de Odoo" del portal y pie de página.
    """,
    'author': "Abrahams",
    'category': 'Uncategorized',
    'version': '1.1',
    'depends': [
        'web',
        'website',
        'portal',
    ],
    'data': [
        'views/report_layout_override.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}