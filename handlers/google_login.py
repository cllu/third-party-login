import webapp2
import config
import json
import urllib
import urllib2
from handlers.base import BaseHandler

class GoogleLoginHandler(BaseHandler):
    def get(self):
        token_request_url = 'https://accounts.google.com/o/oauth2/token'
        user_info_request_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        redirect_uri = 'http://login.chunliang.name/google'
        client_id = config.google['client_id']
        client_secret = config.google['client_secret']
        scope = 'https://www.googleapis.com/auth/userinfo.profile'
        response_type = 'code'

        if self.request.get("code") == '':
            # this is a new application, redirect user to give us permission.
            self.redirect('https://accounts.google.com/o/oauth2/auth?client_id=%s&redirect_uri=%s&scope=%s&response_type=%s' % (client_id, redirect_uri, scope, response_type));
        else:
            # google has return code to us
            if self.request.get("error") != '':
                self.response.out.write("error")
                return
            code = self.request.get("code")
            req = urllib2.Request(token_request_url)
            data = {'code': code,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'}
            req.add_data(urllib.urlencode(data))
            result = urllib2.urlopen(req).read()
            access_token = json.loads(result)['access_token']

            req = '%s?access_token=%s' % (user_info_request_url, access_token)
            result = json.loads(urllib2.urlopen(req).read())
            user = { 'signin': 'true',
                     'from'  : 'google',
                     'name'  : result['name'],
                     'avatar': result['picture'],
                     'link'  : result['link'] }

            self.session['user'] = user
            
            #self.response.out.write(json.dumps(user))
            self.response.out.write('<script type=text/javascript>window.close()</script>')
            
            
