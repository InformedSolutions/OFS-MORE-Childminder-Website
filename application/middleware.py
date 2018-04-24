"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- middleware.py --

@author: Informed Solutions
"""

from re import compile

from django.conf import settings  # import the settings file
from django.http import HttpResponseRedirect, HttpResponseServerError

from .models import Application, UserDetails

COOKIE_IDENTIFIER = '_ofs'


class CustomAuthenticationHandler(object):
    """
    Custom authentication handler to globally protect site with the exception of paths
    tested against regex patterns defined in settings.py
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Default the login url as being authentication exempt
        authentication_exempt_urls = [compile(settings.LOGIN_URL.lstrip('/'))]

        # If further login exempt URLs have been defined in the settings.py file, append these to
        # the collection
        if hasattr(settings, 'AUTHENTICATION_EXEMPT_URLS'):
            authentication_exempt_urls += [compile(expr) for expr in settings.AUTHENTICATION_EXEMPT_URLS]

        # Allow authentication exempt paths straight through middleware function
        if request.path_info == settings.AUTHENTICATION_URL or any(
                m.match(request.path_info) for m in authentication_exempt_urls):
            return self.get_response(request)

        # If path is not exempt, and user cookie does not exist (e.g. a bypass is being attempted) return
        # user to login page
        if self.get_session_user(request) is None:
            return HttpResponseRedirect(settings.AUTHENTICATION_URL)

        # If an application id has been supplied in the query string or post request
        application_id = None

        if request.method == 'GET' and 'id' in request.GET:
            application_id = request.GET.get('id')

        if request.method == 'POST' and 'id' in request.POST:
            application_id = request.POST.get('id')

        # If an application id is present fetch application from store
        if application_id is not None:
            application = Application.objects.get(pk=application_id)
            account = UserDetails.objects.get(application_id=application)
            # Check the email address stored in the session matches that found on the application
            # and if not raise generic exception
            if account.email != self.get_session_user(request):
                raise Exception

        # If request has not been blocked at this point in the execution flow, allow
        # request to continue processing as normal
        response = self.get_response(request)

        session_user = self.get_session_user(request)
        if session_user is not None:
            CustomAuthenticationHandler.create_session(response, session_user)

        return response

    @staticmethod
    def get_cookie_identifier():
        global COOKIE_IDENTIFIER
        return COOKIE_IDENTIFIER

    @staticmethod
    def get_session_user(request):
        if COOKIE_IDENTIFIER not in request.COOKIES:
            return None
        else:
            return request.COOKIES.get(COOKIE_IDENTIFIER)

    @staticmethod
    def create_session(response, email):
        response.set_cookie(COOKIE_IDENTIFIER, email, max_age=1800)

    @staticmethod
    def destroy_session(response):
        response.delete_cookie(COOKIE_IDENTIFIER)


def globalise_url_prefix(request):
    """
    Middleware function to support Django applications being hosted on a
    URL prefixed path (e.g. for use with reverse proxies such as NGINX) rather
    than assuming application available on root index.
    """
    # return URL_PREFIX value defined in django settings.py for use by global view template
    return {'URL_PREFIX': settings.URL_PREFIX}


def globalise_server_name(request):
    """
    Middleware function to pass the server name to the footer
    """
    if hasattr(settings, 'SERVER_LABEL'):
        return {'SERVER_LABEL': settings.SERVER_LABEL}
    else:
        return {'SERVER_LABEL': None}


def hide_costs_link(request):
    """
    Middleware function for hiding the navigation menus costs link depending on an application's status
    """
    application_id = request.GET.get('id')

    # If an application id is not quoted in the request
    if application_id is None:
        return {'HIDE_COSTS': False}

    # Test whether application is in further information status
    application_with_further_information_required = Application.objects.filter(
        pk=application_id, application_status='FURTHER_INFORMATION'
    ).count()

    # If so, hide costs link (see gov uk template for test logic)
    if application_with_further_information_required > 0:
        return {
            'id': application_id,
            'HIDE_COSTS': True,
        }
    else:
        return {
            'id': application_id,
            'HIDE_COSTS': False,
        }


def globalise_authentication_flag(request):
    """
    Middleware function to expose a flag to all templates to determine whether a user is authenticated.
    """
    user_is_authenticated = CustomAuthenticationHandler.get_session_user(request) is not None
    return {'AUTHENTICATED': user_is_authenticated}

