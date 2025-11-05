# -*- coding: utf-8 -*-
{
    'name': "Quitar Facturación (Módulo Personalizado)",

    'summary': """
        Oculta funciones de facturación de Odoo (Backend y E-commerce).
    """,

    'description': """
        Este módulo realiza lo siguiente:
        - Oculta el botón "Crear Factura" en los Pedidos de Venta (Backend).
        - Oculta el menú principal de la aplicación de Facturación (Backend).
        - Oculta la sección "Dirección de Facturación" del checkout (E-commerce).
    """,

    'author': "Miroslav",
    'website': "https://www.tuempresa.com",
    'category': 'Sales/Sales',
    'version': '1.0',

    # --- CAMBIOS IMPORTANTES AQUÍ ---
    'depends': [
        'account',  # <-- Esta es la dependencia para la vista del E-commerce
    ],

    # --- CAMBIOS IMPORTANTES AQUÍ ---
    'data': [
        #'views/sale_order_view.xml',        # El archivo que ya tenías
        'views/menu_views.xml',         # El archivo que ya tenías
       # 'views/website_sale_address_view.xml', # El nuevo archivo
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}