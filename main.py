import webapp2
from webapp2_extras import jinja2
from google.appengine.api import memcache

import config
from handlers.base import BaseHandler
from handlers.google_login import GoogleLoginHandler
from handlers.weibo_login import WeiboLoginHandler
from handlers.qq_login import QQLoginHandler
from handlers.twitter_login import TwitterLoginHandler

class IndexHandler(BaseHandler):
    def get(self):
        user = {}
        try:
            user = self.session['user']
        except:
            pass
        if not user:
            user = {}
        template_values = {
            "user": user,
        }
        self.response.write(self.jinja2.render_template("login.html", **template_values))

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/google', GoogleLoginHandler),
    ('/twitter', TwitterLoginHandler),
    ('/weibo', WeiboLoginHandler),
    ('/qq', QQLoginHandler)
   ], config=config.webapp2_config)

