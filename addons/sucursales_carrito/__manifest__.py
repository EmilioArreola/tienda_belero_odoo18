# -*- coding: utf-8 -*-
{
    'name': "Sucursales en Carrito (Checkout)",
    'summary': """
        Agrega un selector de sucursales en el checkout 
        cuando se elige 'Recoger en tienda'.""",
    'version': '1.0',
    'category': 'Website/eCommerce',
    'depends': [
        'website_sale'  # Dependemos del módulo de eCommerce
    ],
    'data': [
        'views/templates.xml',  # Carga nuestro archivo de vista
    ],
    'assets': {
        'web.assets_frontend': [
            # Registra nuestro nuevo archivo JS
            'sucursales_carrito/static/src/js/sucursales_checkout.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}