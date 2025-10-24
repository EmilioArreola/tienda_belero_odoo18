{
    "name": "Terminator",
    "version": "1.0",
    "depends": ["web"],
    "assets": {
        "web.assets_web": [  # Para el sitio web (frontend)
            "belero_web_custom/static/src/css/hide_menu.css"
        ],
        "web.assets_backend": [  # Para el panel de admin (backend)
            "belero_web_custom/static/src/css/hide_menu.css"
        ]
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}