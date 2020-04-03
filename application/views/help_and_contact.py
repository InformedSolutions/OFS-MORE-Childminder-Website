"""
Method for returning the template for the Help page
"""
from django.shortcuts import render
from ..utils import build_url
from ..models import Application


def help_and_contact(request):
    """
    Renders the help and contact page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Help and Contact template
    """
    application_id_local = request.GET.get('id')

    context = {
        'id': application_id_local
    }

    if application_id_local is not None:
        application = Application.objects.get(pk=application_id_local)
        url_params = {'id': application_id_local, 'get': True}
        status = application.application_status

        # render either confirmation or task list view, depending on if application has been submitted
        if status == 'SUBMITTED':
            return_view = 'Awaiting-Review-View'
            url_params['orderCode'] = str(application.application_reference)
        elif status == 'ARC_REVIEW':
            return_view = 'Awaiting-Review-View'
            url_params['orderCode'] = str(application.application_reference)
        elif status == 'ACCEPTED':
            return_view = 'Accepted-View'
            url_params['orderCode'] = str(application.application_reference)
        else:
            return_view = 'Task-List-View'

        # build url to be passed to the return button
        context['return_url'] = build_url(return_view, get=url_params)

    return render(request, 'help-and-contact.html', context)
