import webapp2
import urllib
import urllib2
import json
from google.appengine.api import urlfetch
import config
from handlers.base import BaseHandler

class WeiboLoginHandler(BaseHandler):    
    def get(self):
        app_key = config.weibo['app_key']
        app_secret = config.weibo['app_secret']
        redirect_uri = 'http://login.chunliang.name/weibo'
        token_request_url = 'https://api.weibo.com/oauth2/access_token'
        uid_request_url = 'https://api.weibo.com/2/account/get_uid.json'
        user_info_request_url = 'https://api.weibo.com/2/users/show.json'

        if self.request.get("code") == '':
            self.redirect('https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s' % (app_key, redirect_uri))
        else:
            if self.request.get("error") != '':
                self.response.out.write("error")
                return
            code = self.request.get("code")

            req = urllib2.Request(token_request_url)
            data = {'code': code,
                   'client_id': app_key,
                   'client_secret': app_secret,
                   'redirect_uri': redirect_uri,
                   'grant_type': 'authorization_code'}
            data = urllib.urlencode(data)
           
            result = urlfetch.fetch(token_request_url, payload=data, method=urlfetch.POST,headers={'Content-Type': 'application/x-www-form-urlencoded'}, validate_certificate=False).content
            access_token = json.loads(result)['access_token']
            #self.response.out.write(result)
            
            req = '%s?access_token=%s' % (uid_request_url, access_token)
            result = urlfetch.fetch(req, validate_certificate=False).content
            uid = json.loads(result)['uid']
            req = '%s?uid=%s&access_token=%s' % (user_info_request_url, uid, access_token)
            result = urlfetch.fetch(req, validate_certificate=False).content
            result = json.loads(result)
            user = { 'signin': 'true',
                     'from'  : 'weibo',
                     'name'  : result['screen_name'],
                     'avatar': result['profile_image_url'],
                     'link'  : result['url'] }

            self.session['user'] = user
            self.response.out.write('<script type=text/javascript>window.close()</script>')
