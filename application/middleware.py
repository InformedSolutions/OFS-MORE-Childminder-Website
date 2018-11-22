"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- middleware.py --
@author: Informed Solutions
"""

from re import compile

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.signing import Signer, BadSignature

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
        session_user = self.get_session_user(request)

        if session_user is None:
            return HttpResponseRedirect(settings.AUTHENTICATION_URL)

        # If an application id has been supplied in the query string or post request
        application_id = None

        if request.method == 'GET' and 'id' in request.GET:
            application_id = request.GET['id']

        if request.method == 'POST' and 'id' in request.POST:
            application_id = request.POST['id']

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
            signer = Signer()
            try:
                return signer.unsign(request.COOKIES.get(COOKIE_IDENTIFIER))
            except BadSignature:
                # the cookie identifier has not been signed
                return None

    @staticmethod
    def create_session(response, email):
        # Set value persisted in cookie with coupled signature to prevent cookie tampering
        signer = Signer()
        signed_email = signer.sign(email)
        response.set_cookie(COOKIE_IDENTIFIER, signed_email, max_age=1800)

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
    if hasattr(settings, 'URL_PREFIX'):
        return {'URL_PREFIX': settings.URL_PREFIX}
    else:
        return {'URL_PREFIX': ''}


def globalise_server_name(request):
    """
    Middleware function to pass the server name to the footer
    """
    if hasattr(settings, 'SERVER_LABEL'):
        return {'SERVER_LABEL': settings.SERVER_LABEL}
    else:
        return {'SERVER_LABEL': None}


def globalise_authentication_flag(request):
    """
    Middleware function to expose a flag to all templates to determine whether a user is authenticated.
    """
    user_is_authenticated = CustomAuthenticationHandler.get_session_user(request) is not None
    return {'AUTHENTICATED': user_is_authenticated}


def register_as_childminder_link_location(request):
    """
    Middleware function to decide the location of the link in the govuk_template page header dependent
    on application status
    """

    if request.method == 'GET' and 'id' in request.GET:
        application_id = request.GET['id']

        if application_id is not None:

            application = Application.objects.get(pk=application_id)

            if application.application_status not in ['ARC_REVIEW', 'CYGNUM_REVIEW', 'SUBMITTED']:

                login_details_status = application.login_details_status
                childcare_type_status = application.childcare_type_status
                personal_details_status = application.personal_details_status

                if login_details_status in ['FLAGGED', 'COMPLETED'] and childcare_type_status in ['FLAGGED', 'COMPLETED'] and personal_details_status in ['FLAGGED', 'COMPLETED']:

                    return {'task_list_link': True,
                            'id': application_id}

    return {'task_list_link': False}
