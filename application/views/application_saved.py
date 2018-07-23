"""
Method returning the template for the Application saved page (for a given application)
"""

from django.shortcuts import render

from ..middleware import *


def application_saved(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Application saved template
    """
    cookie_key = CustomAuthenticationHandler.get_cookie_identifier()
    request.COOKIES[cookie_key] = None
    response = render(request, 'application-saved.html')
    CustomAuthenticationHandler.destroy_session(response)
    return response
