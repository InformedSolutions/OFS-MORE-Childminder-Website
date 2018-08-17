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
    response = render(request, 'application-saved.html')
    CustomAuthenticationHandler.destroy_session(response)
    return response
