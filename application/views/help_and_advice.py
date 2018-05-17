"""
Method for returning the template for the Help page
"""
from django.shortcuts import render
from ..utils import build_url
from ..models import Application


def help_and_advice(request):
    """
    Renders the help and advice page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Help and Advice template
    """
    application_id_local = request.GET.get('id')

    context = {
        'id': application_id_local
    }

    if application_id_local is not None:
        application = Application.objects.get(pk=application_id_local)
        url_params = {'id': application_id_local, 'get': True}

        # render either confirmation or task list view, depending on if application has been submitted
        if application.application_status == 'SUBMITTED':
            return_view = 'Payment-Confirmation'
            url_params['orderCode'] = str(application.order_code)
        else:
            return_view = 'Task-List-View'

        # build url to be passed to the return button
        context['return_url'] = build_url(return_view, get=url_params)

    return render(request, 'help-and-advice.html', context)
