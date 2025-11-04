# -*- coding: utf-8 -*-
{
    'name': "Sucursales Carrito (Checkout)",
    'summary': """
        Agrega un selector de sucursales en el checkout 
        cuando se elige 'Recoger en tienda' Vol 2.0.""",
    'author': "carlita1",
    'version': '1.0',
   'category': 'Website/eCommerce',
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Agregamos 'website' a las dependencias.
    # Esto asegura que nuestro módulo cargue después de 'web' y 'website',
    # lo que debería resolver el problema de 'web.public.widget'.
    'depends': [
        'website_sale',
        'website', # <-- ¡Esta es la línea clave!
    ],
    # --- FIN DE LA CORRECCIÓN ---
    
    'data': [
        'views/templates.xml',  # Carga nuestro archivo de vista
    ],
    
    'assets': {
        'web.assets_frontend': [
            # Mantenemos la forma simple:
            'sucursales_carrito/static/src/js/sucursales_checkout.js',
        ],
    },
    
    'installable': True,
    'application': False,
    'auto_install': False,
}