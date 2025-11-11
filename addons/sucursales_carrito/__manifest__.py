# -*- coding: utf-8 -*-
{
    'name': "Sucursales Carrito (Checkout)",
    'summary': "Selector de sucursales en checkout para Odoo 18",
    'author': "V 2.4.4",  # Actualizado
    'version': '18.0.1.1', 
    'category': 'Website/eCommerce',
    
    'depends': [
        'website_sale',
        'sale_management', 
    ],
    
    'data': [
        'views/templates.xml',
        'views/sale_order_views.xml', 
    ],
    
    'assets': {
        'web.assets_frontend': [
            'sucursales_carrito/static/src/js/sucursales_checkout.js',
            'sucursales_carrito/static/src/css/sucursales_checkout.css',
        ],
    },
    
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}