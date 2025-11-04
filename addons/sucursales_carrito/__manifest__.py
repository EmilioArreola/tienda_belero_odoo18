# -*- coding: utf-8 -*-
{
    'name': "Sucursales Carrito (Checkout)",
    'summary': """
        Agrega un selector de sucursales en el checkout 
        cuando se elige 'Recoger en tienda Vol 2.0'.""",
    'author': "Carlita",
    'version': '1.0',
    'category': 'Website/eCommerce',
    'depends': [
        'website_sale'  # Dependemos del módulo de eCommerce
    ],
    'data': [
        'views/templates.xml',  # Carga nuestro archivo de vista
    ],
    
    # --- INICIO DE LA CORRECCIÓN ---
    'assets': {
        'web.assets_frontend': [
            (
                'after',
                # ESTA ES LA LÍNEA QUE CAMBIAMOS:
                # Usamos un archivo de website_sale como ancla, es más seguro.
                'website_sale/static/src/js/website_sale.js',
                'sucursales_carrito/static/src/js/sucursales_checkout.js'
            ),
        ],
    },
    # --- FIN DE LA CORRECCIÓN ---
    
    'installable': True,
    'application': False,
    'auto_install': False,
}