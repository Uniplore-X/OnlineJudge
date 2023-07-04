from utils.shortcuts import get_env


wp_oauth2_authorize_uri = get_env("wp_oauth2_authorize_uri", "https://labplore.com/oauth/authorize")
wp_oauth2_token_uri = get_env("wp_oauth2_token_uri", "https://labplore.com/oauth/token")
wp_oauth2_userinfo_uri = get_env("wp_oauth2_userinfo_uri", "https://labplore.com/oauth/me")
wp_oauth2_client_id = get_env("wp_oauth2_client_id", "test")
wp_oauth2_client_secret = get_env("wp_oauth2_client_secret", "test")
wp_oauth2_redirect_uri = get_env("wp_oauth2_redirect_uri", "https://oj.labplore.com/api/labplore/wplogin")
wp_oauth2_super_admin_openid = get_env("wp_oauth2_super_admin_openid", "1")
