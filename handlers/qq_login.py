import webapp2
import json
import cgi
from google.appengine.api import urlfetch
import config
from handlers.base import BaseHandler

class QQLoginHandler(BaseHandler):
    def get(self):
        appid = config.qq['app_id']
        appkey = config.qq['app_key']
        redirect_uri = 'http://login.chunliang.name/qq'
        authorize_url = 'https://graph.qq.com/oauth2.0/authorize'
        scope = 'get_user_info'
        token_request_url = 'https://graph.qq.com/oauth2.0/token'
        openid_request_url = 'https://graph.qq.com/oauth2.0/me'
        user_info_request_url = 'https://graph.qq.com/user/get_user_info'
        
        if self.request.get("code") == '':
            # 1. redirect user to grant permission
            self.redirect('%s?response_type=code&client_id=%s&redirect_uri=%s&scope=%s' % (authorize_url, appid, redirect_uri, scope))
        else:
            if self.request.get("error") != '':
                self.response.out.write("error")
                return
            code = self.request.get("code")
            # 2. request access_token
            req = '%s?grant_type=authorization_code&client_id=%s&client_secret=%s&code=%s&redirect_uri=%s' % (token_request_url, appid, appkey, code, redirect_uri)
            # self.response.out.write(req)
            result = urlfetch.fetch(req).content
            parsed_result = cgi.parse_qs(result)
            access_token = parsed_result['access_token'][0]

            # 3. request openID
            req = '%s?access_token=%s' % (openid_request_url, access_token)
            result = urlfetch.fetch(req, validate_certificate=False).content
            result = json.loads(result[result.find('(')+1: result.find(')')])
            openid = result['openid']

            # 4. use openid to get user info
            req = '%s?access_token=%s&oauth_consumer_key=%s&openid=%s' % (user_info_request_url, access_token, appid, openid)
            result = urlfetch.fetch(req).content.decode("utf8")

            result = json.loads(result)
            user = { 'signin': 'true',
                     'from'  : 'qq',
                     'name'  : result['nickname'],
                     'avatar': result['figureurl'],
                     'link'  : '' }

            self.session['user'] = user
            self.response.out.write('<script type=text/javascript>window.close()</script>')

