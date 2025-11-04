# -*- coding: utf-8 -*-
{
    'name': "Sucursales en Carrito (Checkout)",
    'summary': """
        Agrega un selector de sucursales en el checkout 
        cuando se elige 'Recoger en tiendaaa aa'.""",
    'author': "CAAB",
    'version': '1.0',
    'category': 'Website/eCommerce',
    'depends': [
        'website_sale'  # Dependemos del módulo de eCommerce
    ],
    'data': [
        'views/templates.xml',  # Carga nuestro archivo de vista
    ],
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Cambiamos cómo se registran los assets
    'assets': {
        'web.assets_frontend': [
            # Usamos una tupla para definir el orden de carga:
            # (posición, archivo_de_referencia, mi_archivo)
            (
                'after',
                'web/static/src/js/public/public_widget.js',
                'sucursales_carrito/static/src/js/sucursales_checkout.js'
            ),
        ],
    },
    # --- FIN DE LA CORRECCIÓN ---
    
    'installable': True,
    'application': False,
    'auto_install': False,
}