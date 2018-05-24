from django.shortcuts import render
from timeline_logger.models import TimelineLog

from ..models import (Application)


def payment_confirmation(request):
    """
    Method returning the template for the Payment confirmation page (for a given application)
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Payment confirmation template
    """
    application_id_local = request.GET['id']

    variables = {
        'application_id': application_id_local,
        'order_code': request.GET["orderCode"],
    }
    local_app = Application.objects.get(
        application_id=application_id_local)
    local_app.application_status = 'SUBMITTED'
    local_app.save()

    # Payment presents the first true trigger for submission so is logged as submitted at this point
    TimelineLog.objects.create(
        content_object=local_app,
        user=None,
        template='timeline_logger/application_action.txt',
        extra_data={'user_type': 'applicant', 'action': 'submitted by', 'entity': 'application'}
    )

    return render(request, 'payment-confirmation.html', variables)