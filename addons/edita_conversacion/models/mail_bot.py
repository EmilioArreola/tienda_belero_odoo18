from odoo import models, api

class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    @api.model
    def _get_answer(self, record, body, values, command):
        # Obtenemos la respuesta original del sistema
        answer = super(MailBot, self)._get_answer(record, body, values, command)
        
        # Filtramos la marca en cualquier respuesta de texto
        if isinstance(answer, str):
            answer = answer.replace('Odoo', 'Belero')
            answer = answer.replace("Odoo's", "Belero's")
            
        return answer