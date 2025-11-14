# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home

# Solo importar lo que existe
try:
    from odoo.addons.web.controllers.main import Database, Session, Action, DataSet
    HAS_MAIN = True
except ImportError:
    HAS_MAIN = False


class SmartsHome(Home):
    """Heredar el controlador Home para rutas /smarts"""
    
    @http.route('/smarts', type='http', auth="none", website=True)
    def smarts_index(self, *args, **kw):
        return super(SmartsHome, self).index(*args, **kw)
    
    @http.route('/smarts/web', type='http', auth="none")
    def smarts_web_client(self, s_action=None, **kw):
        return super(SmartsHome, self).web_client(s_action, **kw)
    
    @http.route('/smarts/web/login', type='http', auth="none")
    def smarts_web_login(self, redirect=None, **kw):
        return super(SmartsHome, self).web_login(redirect, **kw)
    
    @http.route('/smarts/web/become', type='http', auth="user")
    def smarts_web_become(self, **kw):
        return super(SmartsHome, self).web_become(**kw)


# Solo definir estas clases si existen en main
if HAS_MAIN:
    
    class SmartsSession(Session):
        """Heredar Session para rutas /smarts"""
        
        @http.route('/smarts/web/session/get_session_info', type='json', auth="user")
        def smarts_get_session_info(self):
            return super(SmartsSession, self).get_session_info()
        
        @http.route('/smarts/web/session/authenticate', type='json', auth="none")
        def smarts_authenticate(self, db, login, password, base_location=None):
            return super(SmartsSession, self).authenticate(db, login, password, base_location)
        
        @http.route('/smarts/web/session/destroy', type='json', auth="user")
        def smarts_destroy(self):
            return super(SmartsSession, self).destroy()
        
        @http.route('/smarts/web/session/logout', type='http', auth="none")
        def smarts_logout(self, redirect='/smarts/web'):
            return super(SmartsSession, self).logout(redirect)
    
    
    class SmartsDatabase(Database):
        """Heredar Database para rutas /smarts"""
        
        @http.route('/smarts/web/database/selector', type='http', auth="none")
        def smarts_selector(self, **kw):
            return super(SmartsDatabase, self).selector(**kw)
        
        @http.route('/smarts/web/database/list', type='json', auth="none")
        def smarts_list(self, **kw):
            return super(SmartsDatabase, self).list(**kw)
        
        @http.route('/smarts/web/database/manager', type='http', auth="none")
        def smarts_manager(self, **kw):
            return super(SmartsDatabase, self).manager(**kw)
    
    
    class SmartsAction(Action):
        """Heredar Action para rutas /smarts"""
        
        @http.route('/smarts/web/action/load', type='json', auth="user")
        def smarts_load(self, action_id, additional_context=None):
            return super(SmartsAction, self).load(action_id, additional_context)
        
        @http.route('/smarts/web/action/run', type='json', auth="user")
        def smarts_run(self, action_id):
            return super(SmartsAction, self).run(action_id)
    
    
    class SmartsDataSet(DataSet):
        """Heredar DataSet para rutas /smarts"""
        
        @http.route('/smarts/web/dataset/call_kw/<string:model>/<string:method>', type='json', auth="user")
        def smarts_call_kw(self, model, method, args, kwargs):
            return super(SmartsDataSet, self).call_kw(model, method, args, kwargs)
        
        @http.route('/smarts/web/dataset/call_button', type='json', auth="user")
        def smarts_call_button(self, model, method, args, kwargs):
            return super(SmartsDataSet, self).call_button(model, method, args, kwargs)