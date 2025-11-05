# -*- coding: utf-8 -*-
{
    'name': "Traducción Personalizada (item a producto)",
    'version': '1.0',
    'summary': "Cambia 'item(s)' por 'producto(s)' en toda la web.",
    'category': 'Website',
    
    # Depende de la tienda para cargar la traducción después de ella
    'depends': [
        'website_sale',
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}