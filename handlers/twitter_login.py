import random
import hmac
import cgi
import time
import hashlib
import urllib
import json
import webapp2
from google.appengine.api import urlfetch
from google.appengine.api import memcache

import config
from handlers.base import BaseHandler

class TwitterLoginHandler(BaseHandler):
    def get(self):
        consumer_key = config.twitter['consumer_key']
        consumer_secret = config.twitter['consumer_secret']
        request_token_url = 'https://api.twitter.com/oauth/request_token'
        authorize_url = 'https://api.twitter.com/oauth/authorize'
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        user_info_url = 'https://api.twitter.com/1/account/verify_credentials.json'
        callback_url = 'http://login.chunliang.name/twitter'

        nonce = str(random.getrandbits(64))
        timestamp = str(int(time.time()))

        # 1. acquiring a request token
        if self.request.get('oauth_verifier') == '':
            params = {
                'oauth_callback': callback_url,
                'oauth_consumer_key': consumer_key,
                'oauth_nonce': nonce,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': timestamp,
                'oauth_version': '1.0',
                }
            params_str = "&".join(['%s=%s' % (urllib.quote_plus(k), urllib.quote_plus(params[k])) for k in sorted(params)])
            message =  "&".join(["POST", urllib.quote_plus(request_token_url), urllib.quote_plus(params_str)])
            key = "%s&" % consumer_secret
            signature = hmac.new(key, message, hashlib.sha1)
            digest_base64 = signature.digest().encode("base64").strip()
            params['oauth_signature'] = digest_base64
            
            auth_data = 'OAuth oauth_nonce="%s",oauth_callback="%s",oauth_signature_method="HMAC-SHA1",oauth_timestamp="%s",oauth_consumer_key="%s",oauth_signature="%s",oauth_version="1.0"' % (nonce, urllib.quote_plus(callback_url), timestamp, consumer_key, urllib.quote_plus(digest_base64))
            data = urlfetch.fetch(request_token_url, method="POST", headers={"Authorization": auth_data}).content
            parsed_result = cgi.parse_qs(data)
            oauth_token = parsed_result['oauth_token'][0]
            oauth_token_secret = parsed_result['oauth_token_secret'][0]
            memcache.add(oauth_token, oauth_token_secret, 600)
            req = '%s?oauth_token=%s' % (authorize_url, oauth_token)
            self.redirect(req)
        else:
            # 2. after user verifies, get the access token
            oauth_verifier = self.request.get('oauth_verifier')
            oauth_token = self.request.get('oauth_token')
            # TODO, make sure we can find it in memcache
            oauth_token_secret = memcache.get(oauth_token)
            params = {
                'oauth_consumer_key': consumer_key,
                'oauth_nonce': nonce,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_token': oauth_token,
                'oauth_timestamp': timestamp,
                'oauth_version': '1.0',
                }
            params_str = "&".join(['%s=%s' % (urllib.quote_plus(k), urllib.quote_plus(params[k])) for k in sorted(params)])
            message =  "&".join(["POST", urllib.quote_plus(access_token_url), urllib.quote_plus(params_str)])
            key = "%s&%s" % (consumer_secret, oauth_token_secret)
            signature = hmac.new(key, message, hashlib.sha1)
            digest_base64 = signature.digest().encode("base64").strip()
            params['oauth_signature'] = digest_base64
            
            auth_data = 'OAuth oauth_nonce="%s",oauth_signature_method="HMAC-SHA1",oauth_timestamp="%s",oauth_consumer_key="%s",oauth_token="%s",oauth_verifier="%s",oauth_signature="%s",oauth_version="1.0"' % (nonce, timestamp, consumer_key, oauth_token, oauth_verifier, urllib.quote_plus(digest_base64))

            data = urlfetch.fetch(access_token_url, method="POST", headers={"Authorization": auth_data}).content
            parsed_result = cgi.parse_qs(data)
            access_token = parsed_result['oauth_token'][0]
            access_token_secret = parsed_result['oauth_token_secret'][0]
            
            # 3. reqest user data
            nonce = str(random.getrandbits(64))
            timestamp = str(int(time.time()))
            params = {
                'oauth_consumer_key': consumer_key,
                'oauth_nonce': nonce,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_token': access_token,
                'oauth_timestamp': timestamp,
                'oauth_version': '1.0',
                }
            params_str = "&".join(['%s=%s' % (urllib.quote_plus(k), urllib.quote_plus(params[k])) for k in sorted(params)])
            message =  "&".join(["GET", urllib.quote_plus(user_info_url), urllib.quote_plus(params_str)])
            key = "%s&%s" % (consumer_secret, access_token_secret)
            signature = hmac.new(key, message, hashlib.sha1)
            digest_base64 = signature.digest().encode("base64").strip()
            params['oauth_signature'] = digest_base64
            
            auth_data = 'OAuth oauth_nonce="%s",oauth_signature_method="HMAC-SHA1",oauth_timestamp="%s",oauth_consumer_key="%s",oauth_token="%s",oauth_signature="%s",oauth_version="1.0"' % (nonce, timestamp, consumer_key, access_token, urllib.quote_plus(digest_base64))
            data = urlfetch.fetch(user_info_url, method="GET", headers={"Authorization": auth_data}).content
            data = json.loads(data)
            user = { 
                'signin': 'true',
                'from'  : 'twitter',
                'name'  : data['name'],
                'avatar': data['profile_image_url'],
                'link'  : data['url'] 
                }

            self.session['user'] = user
            self.response.out.write('<script type=text/javascript>window.close()</script>')
