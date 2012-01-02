import os
import random
import base64
import json
import datetime
import time
import webapp2
from webapp2_extras import jinja2
from webapp2_extras import sessions
from google.appengine.api import memcache


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()
    
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)
