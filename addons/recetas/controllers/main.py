from odoo import http

class RecetasWebsite(http.Controller):

    @http.route('/recetas', type='http', auth='public', website=True)
    def recetas_gallery(self, **kw):
        # Debe llamar a la plantilla de página completa
        return http.request.render('recetas.recetas_galeria_template', {})