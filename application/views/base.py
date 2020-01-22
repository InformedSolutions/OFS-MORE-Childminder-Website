"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- views.py --

@author: Informed Solutions
"""

import logging

from django.conf import settings
from django.shortcuts import render

from .. import status
from ..models import Application

# initiate logging
log = logging.getLogger('django.server')


def error_404(request):
    """
    Method returning the 404 error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 404 error template
    """
    data = {}
    return render(request, '404.html', data)


def error_500(request):
    """
    Method returning the 500 error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 500 error template
    """
    data = {}
    return render(request, '500.html', data)


def start_page(request):
    """
    Method returning the template for the start page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered start page template
    """
    context = {'fee': settings.EY_FEE}
    return render(request, 'start-page.html', context)  # 'Start-Page-View'


def awaiting_review(request):
    """
    Method for returning a confirmation view that an application is awaiting ARC review
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered awaiting review saved template
    """
    application_id_local = request.GET["id"]
    application = Application.objects.get(application_id=application_id_local)
    if 'resubmitted' in request.GET.keys():
        resubmitted = request.GET["resubmitted"]
    else:
        resubmitted = '0'
    if resubmitted == '1':
        status.update(application_id_local, 'application_status', 'SUBMITTED')
    variables = {
        'resubmitted': resubmitted,
        'application_id': application_id_local,
        'id': application_id_local,
        'application_reference': application.application_reference
    }
    return render(request, 'awaiting-review.html', variables)


def application_accepted(request):
    """
    Method for returning a confirmation view that an application has been fully submitted
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered application submitted saved template
    """
    application_id_local = request.GET["id"]
    application = Application.objects.get(application_id=application_id_local)
    variables = {
        'application_id': application_id_local,
        'id': application_id_local,
        'application_reference': application.application_reference
    }
    return render(request, 'application-accepted.html', variables)
