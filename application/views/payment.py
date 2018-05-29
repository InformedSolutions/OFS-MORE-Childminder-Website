from django.shortcuts import render
from timeline_logger.models import TimelineLog

from ..models import (Application)
from ..models import (CriminalRecordCheck)
from .. import status

def payment_confirmation(request):
    """
    Method returning the template for the Payment confirmation page (for a given application)
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Payment confirmation template
    """
    application_id_local = request.GET['id']
    try:
        conviction = CriminalRecordCheck.objects.get(application_id=application_id_local).cautions_convictions
    except CriminalRecordCheck.DoesNotExist:
        conviction = False

    variables = {
        'application_id': application_id_local,
        'order_code': request.GET["orderCode"],
        'conviction': conviction,
        'health_status': Application.objects.get(application_id=application_id_local).health_status
    }
    local_app = Application.objects.get(
        application_id=application_id_local)
    status.update(application_id_local, 'declarations_status', 'COMPLETED')
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