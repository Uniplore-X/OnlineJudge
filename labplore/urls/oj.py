from django.conf.urls import url

from ..views.oj import (RedirectWPLoginPageAPI, WPLoginAPI, CheckLoginAPI)

urlpatterns = [
    url(r"^redirect_wplogin/?$", RedirectWPLoginPageAPI.as_view(), name="redirect_wordpress_login_page_api"),
    url(r"^wplogin/?$", WPLoginAPI.as_view(), name="wordpress_login_api"),
    url(r"^check_login/?$", CheckLoginAPI.as_view(), name="check_login_api")
]
