# middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User



class SwitchSessionCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            settings.SESSION_COOKIE_NAME = settings.ADMIN_SITE_SESSION_COOKIE_NAME
        else:
            settings.SESSION_COOKIE_NAME = settings.MAIN_SITE_SESSION_COOKIE_NAME

class CustomAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None

        # Custom authentication logic for main site users
        if not request.user.is_authenticated and 'website_auth' in request.session:
            user = self.get_user_from_session(request.session['website_auth'])
            if user is not None:
                request.user = user

    def get_user_from_session(self, session_key):
        try:
            user = User.objects.get(pk=session_key)
            return user
        except User.DoesNotExist:
            return None