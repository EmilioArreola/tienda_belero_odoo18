# -*- coding: utf-8 -*-
{
    'name': "Sucursales Carrito (Checkout)",
    'summary': "Selector de sucursales en checkout para Odoo 18",
    'author': "v1.6",  # Actualizado
    'version': '18.0.1.1', # Actualizado

    'category': 'Website/eCommerce',
    
    'depends': [
        'website_sale',
        'sale_management',  # <-- NUEVA DEPENDENCIA
    ],
    
    'data': [
        'views/templates.xml',
        'views/sale_order_views.xml', # <-- NUEVO ARCHIVO DE VISTA
    ],
    
    'assets': {
        'web.assets_frontend': [
            'sucursales_carrito/static/src/js/sucursales_checkout.js',
        ],
    },
    
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}