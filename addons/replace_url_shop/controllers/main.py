from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http

class WebsiteSaleCatalogo(WebsiteSale):

    @http.route([
        '/catalogo',
        '/catalogo/page/<int:page>',
        '/catalogo/category/<model("product.public.category"):category>',
    ], type='http', auth="public", website=True, sitemap=True)
    def shop_catalogo(self, **kw):
        return super().shop(**kw)
