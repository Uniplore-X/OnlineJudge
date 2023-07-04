from urllib.parse import urlencode
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import auth
from django.http import HttpResponseRedirect
import requests
from http import HTTPStatus

from utils.api import APIView
from utils.cache import cache
from account.models import User, UserProfile, AdminType, ProblemPermission
from account.decorators import login_required

from labplore import config
from labplore.utils.base_utils import random_unique_code

logger = logging.getLogger(__name__)


class CheckLoginAPI(APIView):
    @login_required
    def post(self, request, **kwargs):
        return self.success("logined")


class RedirectWPLoginPageAPI(APIView):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        data = request.data
        if 'return_uri' in data:
            return_uri = data['return_uri']
        else:
            return_uri = '/'
        request.session['return_uri'] = return_uri
        state = random_unique_code()
        url_query = urlencode({
            'client_id': config.wp_oauth2_client_id,
            'redirect_uri': config.wp_oauth2_redirect_uri,
            'response_type': 'code',
            'scope': 'basic',
            'state': state,
        })

        authorize_uri = f'''{config.wp_oauth2_authorize_uri}?{url_query}'''
        cache.set('wpstate_' + state, 'true', timeout=300)
        result = {
            "authorize_uri": authorize_uri,
        }
        return self.success(result)


class WPLoginAPI(APIView):
    def get(self, request):
        data = request.data
        if 'code' not in data:
            return self.error("code required")
        elif 'state' not in data:
            return self.error("state required")

        code = data['code']
        state = data['state']
        if cache.get('wpstate_' + state) != 'true':
            return self.error("state error")
        else:
            # 获取access_token
            body_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': config.wp_oauth2_client_id,
                'client_secret': config.wp_oauth2_client_secret,
                'redirect_uri': config.wp_oauth2_redirect_uri,
                'state': state,
            }
            token_uri = f'''{config.wp_oauth2_token_uri}'''
            response = requests.post(token_uri, data=body_data, allow_redirects=False)
            if response.status_code != HTTPStatus.OK.value and response.status_code != HTTPStatus.BAD_REQUEST.value:
                return self.error("get access_token error: code=" + str(response.status_code))
            else:
                token_result = response.json()
                if 'access_token' not in token_result or 'error' in token_result:
                    logger.debug('get access_token failed: ' + response.text)
                    err_data = {
                        'errmsg': 'get access_token failed',
                        'data': token_result
                    }
                    return self.error(err_data)
                else:
                    access_token = token_result['access_token']

            # 获取用户信息
            userinfo_uri = f'''{config.wp_oauth2_userinfo_uri}?access_token={access_token}'''
            response = requests.get(userinfo_uri, allow_redirects=False)
            if response.status_code != HTTPStatus.OK.value:
                err_data = {
                    'errmsg': 'get user info error',
                    'response': response.text
                }
                return self.error(err_data)
            else:
                logger.debug('user info: ' + response.text)
                userinfo_result = response.json()
                user_openid = userinfo_result['ID']
                user_name = userinfo_result['display_name'] if 'display_name' in userinfo_result else userinfo_result[
                    'user_nicename']
                user_email = userinfo_result['user_email'] if 'user_email' in userinfo_result else None
                is_super_admin = False
                is_admin = False
                if "capabilities" in userinfo_result:
                    capabilities = userinfo_result["capabilities"]
                    is_admin = (capabilities['administrator'] is True) if 'administrator' in capabilities else False

                if is_admin and user_openid == config.wp_oauth2_super_admin_openid:
                    is_super_admin = True

                # 添加或修改用户
                try:
                    user = User.objects.get(luid=user_openid)
                except User.DoesNotExist:
                    user = None

                if user is None:
                    user = User.objects.create(username=user_name, email=user_email, luid=user_openid)
                    user.set_password(random_unique_code())
                    if is_super_admin:
                        user.admin_type = AdminType.SUPER_ADMIN
                        user.problem_permission = ProblemPermission.ALL
                    elif is_admin:
                        user.admin_type = AdminType.ADMIN
                        user.problem_permission = ProblemPermission.ALL
                    else:
                        user.admin_type = AdminType.REGULAR_USER
                        user.problem_permission = ProblemPermission.OWN
                    user.save()
                    UserProfile.objects.create(user=user)
                else:
                    user.username = user_name
                    user.email = user_email
                    if is_super_admin:
                        user.admin_type = AdminType.SUPER_ADMIN
                        user.problem_permission = ProblemPermission.ALL
                    elif is_admin:
                        user.admin_type = AdminType.ADMIN
                        user.problem_permission = ProblemPermission.ALL
                    else:
                        user.admin_type = AdminType.REGULAR_USER
                        user.problem_permission = ProblemPermission.OWN
                    user.save()

                auth.login(request, user)

                return_uri = request.session.get('return_uri', '/')

                return HttpResponseRedirect(return_uri)
