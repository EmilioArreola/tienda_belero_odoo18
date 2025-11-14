from odoo import models
from odoo.http import request

class HttpRewrite(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _dispatch(cls, endpoint, *args):
        env = request.env['ir.config_parameter'].sudo()

        search_str = env.get_param('web.replace.from', 'odoo')
        replace_str = env.get_param('web.replace.to', 'smarts')

        if request and request.httprequest:
            url_root = request.httprequest.url_root
            if search_str in url_root:
                request.httprequest.url_root = url_root.replace(search_str, replace_str)

        return super(HttpRewrite, cls)._dispatch(endpoint, *args)

    @classmethod
    def make_url(cls, url, *args, **kwargs):
        env = request.env['ir.config_parameter'].sudo()

        search_str = env.get_param('web.replace.from', 'odoo')
        replace_str = env.get_param('web.replace.to', 'smarts')

        if url.startswith('/' + search_str):
            url = url.replace('/' + search_str, '/' + replace_str, 1)

        return super(HttpRewrite, cls).make_url(url, *args, **kwargs)
