from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http

class WebsiteSaleCatalogo(WebsiteSale):

    @http.route([
        '/catalogo',
        '/catalogo/page/<int:page>',
        '/catalogo/category/<model("product.public.category"):category>',
        '/catalogo/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=True)
    def shop_catalogo(self, page=0, category=None, search='', **kw):
        return super().shop(page=page, category=category, search=search, **kw)
    @http.route('/catalogo/<model("product.template"):product>', type='http', auth="public", website=True, sitemap=True)
    def product_catalogo(self, product, **kw):
        return super().product(product=product, **kw)