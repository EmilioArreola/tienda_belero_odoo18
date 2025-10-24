{
    "name": "Terminator",
    "version": "1.0",
    "depends": ["web"],
    "data": [
        # Las plantillas de assets (XML) no van aquí
    ],
    "assets": {
        # --- CORRECCIÓN IMPORTANTE PARA ODOO 18 ---
        # El bundle principal del backend ahora se llama 'web.assets_web'
        "web.assets_web": [
            
            # 1. ¡IMPORTANTE! Hemos eliminado la línea del .js
            #    ("static/src/js/hide_user_menu_items.js")
            #    porque ese archivo no existe y causaba el error.
            
            # 2. Solo dejamos el archivo XML que sí existe:
            "views/remove_odoo_branding.xml"
        ]
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}