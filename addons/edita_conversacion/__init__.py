from . import models

def post_init_hook(env):
    """
    Usamos SQL directo para limpiar los mensajes existentes de OdooBot
    y evitar el KeyError de ir.translation en Odoo 18.
    """
    # 1. Limpiamos los mensajes ya enviados en los chats
    query_messages = """
        UPDATE mail_message 
        SET body = REPLACE(body, 'Odoo', 'Belero') 
        WHERE body LIKE '%Odoo%';
    """
    env.cr.execute(query_messages)

    # 2. Intentamos renombrar al OdooBot automáticamente si existe
    query_bot_name = """
        UPDATE res_partner 
        SET name = 'BeleroBot' 
        WHERE name = 'OdooBot';
    """
    env.cr.execute(query_bot_name)