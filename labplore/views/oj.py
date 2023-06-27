from urllib.parse import urlencode
import random
import sys
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect
import requests
from requests import Response
from http import HTTPStatus

from utils.api import APIView
from utils.cache import cache
from labplore import config

logger = logging.getLogger(__name__)

class RedirectWPLoginPageAPI(APIView):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        redirect_uri = urlencode(config.wp_oauth2_redirect_uri)
        state = str(random.randint(1000000, sys.maxsize))
        authorize_uri = f'''{config.wp_oauth2_authorize_uri}?client_id={config.wp_oauth2_client_id}&redirect_uri={redirect_uri}&response_type=code&scope=basic&state={state}'''
        cache.set('wpstate_' + state, 'true', timeout=300)
        result = {
            "authorize_uri": authorize_uri,
        }
        return self.success(result)


class WPLoginAPI(APIView):
    def get(self, request):
        data = request.data
        code = data['code']
        state = data['state']
        if cache.get('wpstate_' + state) != 'true':
            return self.error("state error")
        else:
            # 获取access_token
            token_uri = f'''{config.wp_oauth2_token_uri}?grant_type=authorization_code&code={code}&client_id={config.wp_oauth2_client_id}&client_secret={config.wp_oauth2_client_secret}'''
            response = requests.post(token_uri)
            if response.status_code != HTTPStatus.OK.value:
                return self.error("get access_token error")
            else:
                token_result = response.json()
                if token_result['access_token'] is None:
                    return self.error("get access_token failed")
                else:
                    access_token = token_result['access_token']

            # 获取用户信息
            userinfo_uri = f'''{config.wp_oauth2_userinfo_uri}?access_token={access_token}'''
            response = requests.get(userinfo_uri)
            if response.status_code != HTTPStatus.OK.value:
                return self.error("get user info error")
            else:
                logger.debug('user info: ' + response.text)
                userinfo_result = response.json()
                username = userinfo_result['username']
                email = userinfo_result['email']
                userid = userinfo_result['ID']
                return self.error("TODO")

