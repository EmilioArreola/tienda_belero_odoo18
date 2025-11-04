# -*- coding: utf-8 -*-
{
    'name': "Sucursales Carrito (Checkout)",
    'summary': "Selector de sucursales en checkout para Odoo 18",
    'author': "v2.2",
    'version': '18.0.1.0',
    'category': 'Website/eCommerce',
    
    'depends': [
        'website_sale',
    ],
    
    'data': [
        'views/templates.xml',
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
